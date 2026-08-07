#!/usr/bin/env python3
"""SHA-256 ingest cache: skip unchanged sources.

Ledger: ``.llm-wiki/ingest/cache.json``

Commands:
  lookup <path>           Print hit/miss JSON for a source file
  record [path] ...       Record a successful ingest; accepts lookup --sha256 after cleanup
  list                    List cache entries
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
try:
    from cross_platform_lock import ExclusiveFileLock
except ModuleNotFoundError:  # Imported by tests as scripts.ingest_cache.
    from scripts.cross_platform_lock import ExclusiveFileLock

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = ROOT / ".llm-wiki" / "ingest" / "cache.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ACTOR = re.compile(r"^(?:human:[^\s:]+|process:[^\s:]+|[^\s/]+/[^\s/]+)$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_cache(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"version": 1, "entries": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"invalid cache root: {path}")
    entries = data.get("entries")
    if not isinstance(entries, dict):
        data["entries"] = {}
    data.setdefault("version", 1)
    return data


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def resolve_input(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def artifacts_present(entry: dict[str, Any]) -> bool:
    archive_slug = entry.get("archive_slug")
    source_page = entry.get("source_page")
    if not isinstance(archive_slug, str) or not archive_slug.strip():
        return False
    archive = ROOT / "raw" / "sources" / f"{archive_slug}.md"
    if not archive.is_file():
        return False
    receipt = entry.get("analysis_receipt")
    if receipt is not None:
        if not isinstance(receipt, dict) or receipt.get("source_sha256") != sha256_file(archive):
            return False
    if isinstance(source_page, str) and source_page.strip():
        page = ROOT / source_page
        if not page.is_file():
            return False
    return True


def cmd_lookup(args: argparse.Namespace) -> int:
    source = resolve_input(args.path)
    if not source.is_file():
        print(json.dumps({"ok": False, "error": f"not a file: {source}"}), file=sys.stderr)
        return 1
    digest = sha256_file(source)
    cache = load_cache(Path(args.cache) if args.cache else DEFAULT_CACHE)
    entry = cache["entries"].get(digest)
    hit = isinstance(entry, dict) and artifacts_present(entry) and not args.force
    payload = {
        "ok": True,
        "hit": hit,
        "sha256": digest,
        "path": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
        "force": bool(args.force),
        "entry": entry if isinstance(entry, dict) else None,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if hit or not args.require_miss else 2


def cmd_record(args: argparse.Namespace) -> int:
    digest = getattr(args, "sha256", None)
    source_name = getattr(args, "original_name", None)
    source_path = getattr(args, "path", None)
    if digest:
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            print("ingest-cache: --sha256 must be a lowercase SHA-256 digest", file=sys.stderr)
            return 1
        digest = digest.lower()
        if not source_name and source_path:
            source_name = resolve_input(source_path).name
        if not source_name:
            print("ingest-cache: --original-name is required with --sha256", file=sys.stderr)
            return 1
    else:
        if not source_path:
            print("ingest-cache: path is required unless --sha256 is supplied", file=sys.stderr)
            return 1
        source = resolve_input(source_path)
        if not source.is_file():
            print(f"ingest-cache: not a file: {source}", file=sys.stderr)
            return 1
        digest = sha256_file(source)
        source_name = source.name
    cache_path = Path(args.cache) if args.cache else DEFAULT_CACHE
    entry = {
        "sha256": digest,
        "archive_slug": args.archive_slug,
        "source_page": args.source_page,
        "original_name": source_name,
        "ingested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    receipt = getattr(args, "analysis_receipt", None)
    if receipt:
        if not isinstance(receipt, str) or not SHA256.fullmatch(receipt):
            print("ingest-cache: --analysis-receipt must be a lowercase SHA-256 digest", file=sys.stderr)
            return 1
        source_digest = getattr(args, "analysis_source_sha256", None)
        if not isinstance(source_digest, str) or not SHA256.fullmatch(source_digest):
            print("ingest-cache: --analysis-source-sha256 must be a lowercase SHA-256 digest", file=sys.stderr)
            return 1
        generated_by = getattr(args, "analysis_generated_by", None)
        generated_at = getattr(args, "analysis_generated_at", None)
        try:
            valid_time = isinstance(generated_at, str) and bool(generated_at.strip()) and datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except ValueError:
            valid_time = None
        if not isinstance(generated_by, str) or not ACTOR.fullmatch(generated_by) or not valid_time:
            print("ingest-cache: analysis receipt requires a valid actor and ISO --analysis-generated-at", file=sys.stderr)
            return 1
        entry["analysis_receipt"] = {"version": str(getattr(args, "analysis_version", "1")), "sha256": receipt, "source_sha256": source_digest, "generated_by": generated_by, "generated_at": generated_at}
    with ExclusiveFileLock(cache_path):
        cache = load_cache(cache_path)
        cache["entries"][digest] = entry
        atomic_write(cache_path, json.dumps(cache, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"ok": True, "recorded": entry}, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    cache = load_cache(Path(args.cache) if args.cache else DEFAULT_CACHE)
    print(json.dumps(cache, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache",
        help="override cache path (default: .llm-wiki/ingest/cache.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    lookup = sub.add_parser("lookup", help="Look up a source file by SHA-256")
    lookup.add_argument("path", help="Source file path")
    lookup.add_argument(
        "--force",
        action="store_true",
        help="Treat as miss even when cache hits",
    )
    lookup.add_argument(
        "--require-miss",
        action="store_true",
        help="Exit 2 when cache hit (useful for shell gates)",
    )
    lookup.set_defaults(func=cmd_lookup)

    record = sub.add_parser("record", help="Record a successful ingest")
    record.add_argument("path", nargs="?", help="Source file path that was ingested")
    record.add_argument("--sha256", help="Digest returned by lookup; permits recording after cleanup")
    record.add_argument("--original-name", help="Original filename (required with --sha256 when no path remains)")
    record.add_argument("--archive-slug", required=True, help="raw/sources/<slug>.md stem")
    record.add_argument(
        "--source-page",
        required=True,
        help="wiki/sources/<page>.md relative to repo root",
    )
    record.add_argument("--analysis-receipt", help="SHA-256 of the private two-stage analysis file")
    record.add_argument("--analysis-version", default="1", help="Analysis receipt schema version")
    record.add_argument("--analysis-source-sha256", help="SHA-256 of raw/sources canonical archive")
    record.add_argument("--analysis-generated-by", help="Actor that completed the private analysis")
    record.add_argument("--analysis-generated-at", help="ISO 8601 analysis completion time")
    record.set_defaults(func=cmd_record)

    listed = sub.add_parser("list", help="Print the cache ledger")
    listed.set_defaults(func=cmd_list)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, RuntimeError, json.JSONDecodeError, ValueError) as error:
        print(f"ingest-cache: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
