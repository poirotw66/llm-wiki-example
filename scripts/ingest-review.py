#!/usr/bin/env python3
"""Append or close async human-review items outside the OKF bundle."""
from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS = str(Path(__file__).resolve().parent)
if _SCRIPTS not in sys.path:  # scripts/ uses hyphenated, unimportable filenames.
    sys.path.append(_SCRIPTS)

from _common import ROOT, Paths, atomic_write
from cross_platform_lock import ExclusiveFileLock

#: Repository holding the queue.  ``configure`` repoints it in one call.
PATHS = Paths(ROOT)
ACTIONS = ("human_verify", "create_page", "deep_research", "governance", "skip")
SKELETON = """# Review Queue

Async human-in-the-loop items. Ingest／Lint may append here without blocking wiki writes.
Close items with ``python3 scripts/ingest-review.py close --id <id>``.

## Open

## Done
"""


def configure(root: Path | str) -> Paths:
    """Point the review queue at ``root``."""
    global PATHS
    PATHS = Paths(Path(root))
    return PATHS


def ensure_queue(path: Path) -> str:
    if not path.is_file():
        atomic_write(path, SKELETON)
    return path.read_text(encoding="utf-8")


def queue_path(args: argparse.Namespace) -> Path:
    return Path(args.queue) if args.queue else PATHS.review_queue


def cmd_append(args: argparse.Namespace) -> int:
    path = queue_path(args)
    item_id = args.id or uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"- [ ] id: {item_id} | {args.source} | {args.title}",
        f"  - reason: {args.reason}",
        f"  - suggested_action: {args.action}",
        *[f"  - related: `{item}`" for item in args.related or []],
        f"  - created: {now}",
    ]
    block = "\n".join(lines) + "\n\n"
    with ExclusiveFileLock(path):
        text = ensure_queue(path)
        if "## Open" not in text or "## Done" not in text:
            print("ingest-review: queue must contain ## Open and ## Done", file=sys.stderr)
            return 1
        open_at, done_at = text.index("## Open"), text.index("## Done")
        insert_at = open_at + len(text[open_at:done_at].rstrip()) + 1
        updated = text[:insert_at] + "\n" + block + text[insert_at:].lstrip("\n")
        atomic_write(path, updated if updated.endswith("\n") else updated + "\n")
    print(f"appended id={item_id} -> {PATHS.display(path)}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    path = queue_path(args)
    with ExclusiveFileLock(path):
        lines = ensure_queue(path).splitlines(keepends=True)
        start_i = next((i for i, line in enumerate(lines) if line.startswith(f"- [ ] id: {args.id} |")), None)
        if start_i is None:
            print(f"ingest-review: open id not found: {args.id}", file=sys.stderr)
            return 1
        end_i = start_i + 1
        while end_i < len(lines) and lines[end_i].startswith(("  ", "\t")):
            end_i += 1
        block = lines[start_i:end_i]
        block[0] = block[0].replace("- [ ] ", "- [x] ", 1)
        block.append(f"  - closed: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
        new_lines = lines[:start_i] + lines[end_i:]
        done_i = next(i for i, line in enumerate(new_lines) if line.startswith("## Done")) + 1
        atomic_write(path, "".join(new_lines[:done_i] + block + new_lines[done_i:]))
    print(f"closed id={args.id}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    path = queue_path(args)
    with ExclusiveFileLock(path):
        print(ensure_queue(path))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", help="override queue path")
    sub = parser.add_subparsers(dest="command", required=True)
    append = sub.add_parser("append", help="Append an open review item")
    append.add_argument("--title", required=True)
    append.add_argument("--reason", required=True)
    append.add_argument("--source", default="ingest")
    append.add_argument("--action", choices=ACTIONS, default="human_verify")
    append.add_argument("--related", action="append", default=[])
    append.add_argument("--id")
    append.set_defaults(func=cmd_append)
    close = sub.add_parser("close", help="Move an open item to Done")
    close.add_argument("--id", required=True)
    close.set_defaults(func=cmd_close)
    listed = sub.add_parser("list", help="Print the queue")
    listed.set_defaults(func=cmd_list)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except OSError as error:
        print(f"ingest-review: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
