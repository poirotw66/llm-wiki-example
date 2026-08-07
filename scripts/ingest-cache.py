#!/usr/bin/env python3
"""SHA-256 ingest cache: skip unchanged sources.

Ledger: ``.llm-wiki/ingest/cache.json``

Commands:
  lookup <path>           Print hit/miss JSON for a source file
  record <path> ...       Record a successful ingest
  list                    List cache entries
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = ROOT / ".llm-wiki" / "ingest" / "cache.json"


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


def save_cache(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


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
    source = resolve_input(args.path)
    if not source.is_file():
        print(f"ingest-cache: not a file: {source}", file=sys.stderr)
        return 1
    digest = sha256_file(source)
    cache_path = Path(args.cache) if args.cache else DEFAULT_CACHE
    cache = load_cache(cache_path)
    entry = {
        "sha256": digest,
        "archive_slug": args.archive_slug,
        "source_page": args.source_page,
        "original_name": source.name,
        "ingested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    cache["entries"][digest] = entry
    save_cache(cache_path, cache)
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
    record.add_argument("path", help="Source file path that was ingested")
    record.add_argument("--archive-slug", required=True, help="raw/sources/<slug>.md stem")
    record.add_argument(
        "--source-page",
        required=True,
        help="wiki/sources/<page>.md relative to repo root",
    )
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
