#!/usr/bin/env python3
"""CI admission checks for secrets and immutable raw archives.

The approval manifest stores metadata and a content digest, never source text.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = str(Path(__file__).resolve().parent)
if _SCRIPTS not in sys.path:  # scripts/ uses hyphenated, unimportable filenames.
    sys.path.append(_SCRIPTS)

from _common import ROOT, git, sha256_file

DEFAULT_MANIFEST = ROOT / "governance" / "raw-approvals.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
OWNER = re.compile(r"^(?:team|human|process):[^\s:]+$")
SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("generic credential assignment", re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}")),
)


def relevant_paths(base: str | None) -> list[tuple[str, str]]:
    """Return candidate status/path pairs, including the initial-commit case."""
    if not base:
        names = set(git("ls-files").splitlines())
        names.update(git("ls-files", "--others", "--exclude-standard").splitlines())
        return [("A", path) for path in sorted(names) if path]
    result: list[tuple[str, str]] = []
    for line in git("diff", "--name-status", "-M", "-C", f"{base}...HEAD").splitlines():
        fields = line.split("\t")
        if len(fields) < 2:
            continue
        status = fields[0]
        # R/C lines are status, old path, new path; inspect the new content.
        result.append((status, fields[-1]))
    return result


def load_manifest(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("approvals"), list):
        raise ValueError("manifest must be an object with an approvals list")
    result: dict[str, dict[str, Any]] = {}
    for item in data["approvals"]:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ValueError("each approval must be an object with path")
        if item["path"] in result:
            raise ValueError(f"duplicate approval path: {item['path']}")
        result[item["path"]] = item
    return result


def approval_issue(path: str, item: dict[str, Any] | None, content_sha256: str) -> str | None:
    if item is None:
        return f"new raw archive lacks governance approval: {path}"
    required = ("classification", "owner", "approved_by", "approved_at", "contains_pii", "redaction", "source_sha256")
    missing = [key for key in required if key not in item or item[key] in (None, "")]
    if missing:
        return f"governance approval missing {', '.join(missing)}: {path}"
    if item["classification"] not in {"public", "internal"}:
        return f"raw archive classification is not Git-admissible: {path}"
    if not isinstance(item["owner"], str) or not OWNER.fullmatch(item["owner"]):
        return f"raw archive owner must be team:<id>, human:<id>, or process:<id>: {path}"
    if item["contains_pii"] is not False or item["redaction"] != "none":
        return f"raw archive requires PII/redaction review outside Git: {path}"
    if not isinstance(item["approved_by"], str) or not re.fullmatch(r"human:[^\s:]+", item["approved_by"]):
        return f"raw archive approval must be human:<id>: {path}"
    if not isinstance(item["approved_at"], str):
        return f"raw archive approved_at must be an ISO date: {path}"
    try:
        dt.date.fromisoformat(item["approved_at"])
    except ValueError:
        return f"raw archive approved_at must be an ISO date: {path}"
    if not isinstance(item["source_sha256"], str) or not SHA256.fullmatch(item["source_sha256"]):
        return f"raw archive source_sha256 must be a lowercase SHA-256 digest: {path}"
    if item["source_sha256"] != content_sha256:
        return f"raw archive source_sha256 does not match file content: {path}"
    return None


def scan(path: Path) -> list[str]:
    if not path.is_file() or path.stat().st_size > 10 * 1024 * 1024:
        return []
    return [name for name, pattern in SECRET_PATTERNS if pattern.search(path.read_text(encoding="utf-8", errors="ignore"))]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Git base revision; omitted means scan all tracked and untracked files")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    args = parser.parse_args(argv)
    try:
        approvals, errors = load_manifest(Path(args.manifest)), []
        for status, path in relevant_paths(args.base):
            if status.startswith("D"):
                continue
            candidate = ROOT / path
            for finding in scan(candidate):
                errors.append(f"possible {finding}: {path}")
            requires_approval = (not args.base or status.startswith(("A", "R", "C"))) and path.startswith("raw/") and not path.endswith(".gitkeep")
            if requires_approval and candidate.is_file():
                issue = approval_issue(path, approvals.get(path), sha256_file(candidate))
                if issue:
                    errors.append(issue)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"governance-gate: {error}", file=sys.stderr)
        return 1
    if errors:
        print("governance-gate: " + "\n".join(errors), file=sys.stderr)
        return 1
    print("governance-gate: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
