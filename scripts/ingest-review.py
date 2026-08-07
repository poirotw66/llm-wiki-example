#!/usr/bin/env python3
"""Append or close items on the async human review queue.

Queue file: ``wiki/review/queue.md`` (not an OKF Concept; reserved name ``queue.md``).

Commands:
  append --title ... --reason ... [--action ...] [--related path]*
  close --id ...
  list
"""
from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "wiki" / "review" / "queue.md"
ACTIONS = ("human_verify", "create_page", "deep_research", "governance", "skip")

SKELETON = """# Review Queue

Async human-in-the-loop items. Ingest／Lint may append here without blocking wiki writes.
Close items with ``python3 scripts/ingest-review.py close --id <id>``.

## Open

## Done
"""


def ensure_queue(path: Path) -> str:
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(SKELETON, encoding="utf-8")
    return path.read_text(encoding="utf-8")


def cmd_append(args: argparse.Namespace) -> int:
    path = Path(args.queue) if args.queue else DEFAULT_QUEUE
    text = ensure_queue(path)
    if "## Open" not in text or "## Done" not in text:
        print("ingest-review: queue.md must contain ## Open and ## Done", file=sys.stderr)
        return 1
    item_id = args.id or uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    related = args.related or []
    lines = [
        f"- [ ] id: {item_id} | {args.source} | {args.title}",
        f"  - reason: {args.reason}",
        f"  - suggested_action: {args.action}",
    ]
    lines.extend(f"  - related: `{item}`" for item in related)
    lines.append(f"  - created: {now}")
    block = "\n".join(lines) + "\n\n"
    open_at = text.index("## Open")
    done_at = text.index("## Done")
    open_section = text[open_at:done_at]
    insert_at = open_at + len(open_section.rstrip()) + 1
    updated = text[:insert_at] + "\n" + block + text[insert_at:].lstrip("\n")
    if not updated.endswith("\n"):
        updated += "\n"
    path.write_text(updated, encoding="utf-8")
    print(f"appended id={item_id} -> {path.relative_to(ROOT)}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    path = Path(args.queue) if args.queue else DEFAULT_QUEUE
    lines = ensure_queue(path).splitlines(keepends=True)
    start_i: int | None = None
    end_i: int | None = None
    for index, line in enumerate(lines):
        if line.startswith(f"- [ ] id: {args.id} |"):
            start_i = index
            end_i = index + 1
            while end_i < len(lines) and (
                lines[end_i].startswith("  ") or lines[end_i].startswith("\t")
            ):
                end_i += 1
            break
    if start_i is None or end_i is None:
        print(f"ingest-review: open id not found: {args.id}", file=sys.stderr)
        return 1
    block_lines = lines[start_i:end_i]
    block_lines[0] = block_lines[0].replace("- [ ] ", "- [x] ", 1)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not any("closed:" in line for line in block_lines):
        suffix = "" if block_lines[-1].endswith("\n") else "\n"
        block_lines.append(f"  - closed: {now}\n" if suffix == "" else f"{suffix}  - closed: {now}\n")
        if not block_lines[-2].endswith("\n"):
            block_lines[-2] = block_lines[-2] + "\n"
    new_lines = lines[:start_i] + lines[end_i:]
    done_index = next(i for i, line in enumerate(new_lines) if line.startswith("## Done"))
    insert = done_index + 1
    while insert < len(new_lines) and new_lines[insert].strip() == "":
        insert += 1
    path.write_text("".join(new_lines[:insert] + block_lines + new_lines[insert:]), encoding="utf-8")
    print(f"closed id={args.id}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    path = Path(args.queue) if args.queue else DEFAULT_QUEUE
    print(ensure_queue(path))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", help="override queue path")
    sub = parser.add_subparsers(dest="command", required=True)

    append = sub.add_parser("append", help="Append an open review item")
    append.add_argument("--title", required=True)
    append.add_argument("--reason", required=True)
    append.add_argument("--source", default="ingest", help="originating operation")
    append.add_argument("--action", choices=ACTIONS, default="human_verify")
    append.add_argument("--related", action="append", default=[])
    append.add_argument("--id", help="optional stable id")
    append.set_defaults(func=cmd_append)

    close = sub.add_parser("close", help="Move an open item to Done")
    close.add_argument("--id", required=True)
    close.set_defaults(func=cmd_close)

    listed = sub.add_parser("list", help="Print the queue file")
    listed.set_defaults(func=cmd_list)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
