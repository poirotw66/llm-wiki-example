#!/usr/bin/env python3
"""Delete an ingest input copy after archive targets exist."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTECTED_DIRS = (
    ROOT / "raw/originals",
    ROOT / "raw/sources",
    ROOT / "raw/assets",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Delete an ingest input copy after archive targets exist."
    )
    parser.add_argument("input_path", help="Original ingest input to remove")
    parser.add_argument(
        "--archive",
        dest="archives",
        action="append",
        required=True,
        help="Archive path that must already exist; repeatable",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the action without deleting the file",
    )
    return parser


def resolve_repo_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def is_protected(path: Path) -> bool:
    return any(path.is_relative_to(directory) for directory in PROTECTED_DIRS)


def validate_input(input_path: Path) -> None:
    if not input_path.exists():
        raise ValueError(f"input not found: {input_path}")
    if input_path.is_dir():
        raise ValueError(f"refuse to delete directory: {input_path}")
    if not input_path.is_relative_to(ROOT):
        raise ValueError(f"input is outside repo: {input_path}")
    if is_protected(input_path):
        raise ValueError(f"refuse to delete archived file: {input_path}")


def validate_archives(archives: list[Path]) -> None:
    missing = [str(path) for path in archives if not path.is_file()]
    if missing:
        raise ValueError("missing archive target(s): " + ", ".join(missing))


def cleanup_input(input_path: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"dry-run: would delete {input_path.relative_to(ROOT)}")
        return
    input_path.unlink()
    print(f"deleted {input_path.relative_to(ROOT)}")


def main() -> int:
    args = build_parser().parse_args()
    input_path = resolve_repo_path(args.input_path)
    archives = [resolve_repo_path(path) for path in args.archives]
    try:
        validate_input(input_path)
        validate_archives(archives)
    except ValueError as error:
        print(f"ingest-cleanup: {error}", file=sys.stderr)
        return 1
    cleanup_input(input_path, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
