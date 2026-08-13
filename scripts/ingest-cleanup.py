#!/usr/bin/env python3
"""Safely remove an ingest input only after its immutable archives are verified.

The archive contract is deliberately narrow: an input may only be removed from
``raw/inbox`` or from the repository root, and its byte-identical original plus
the resulting canonical Markdown source must both already exist.  Deletion is
an explicit action (``--confirm``); without it this command is a dry run.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_SCRIPTS = str(Path(__file__).resolve().parent)
if _SCRIPTS not in sys.path:  # scripts/ uses hyphenated, unimportable filenames.
    sys.path.append(_SCRIPTS)

from _common import ROOT, Paths, sha256_file

#: Repository under cleanup.  ``configure`` repoints every location at once.
PATHS = Paths(ROOT)

#: Directories that never hold a deletable ingest input.  Stored as names so
#: the protected set cannot fall out of step with the configured root.
PROTECTED_DIR_NAMES = (".git", "config", "docs", "raw", "scripts", "skills", "tests", "wiki")
INPUT_SUFFIXES = {
    ".md", ".txt", ".docx", ".pdf", ".ppt", ".pptx", ".xlsx",
    ".png", ".jpg", ".jpeg", ".webp",
}
PROTECTED_ROOT_FILES = {
    "AGENTS.md", "README.md", "SKILL.md", "pyproject.toml", "uv.lock",
    ".gitignore", ".python-version",
}


def configure(root: Path | str) -> Paths:
    """Point every location at ``root``; returns the resulting layout."""
    global PATHS
    PATHS = Paths(Path(root))
    return PATHS


def protected_dirs() -> tuple[Path, ...]:
    return tuple(PATHS.root / name for name in PROTECTED_DIR_NAMES)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely delete an ingest input after both archive records are verified."
    )
    parser.add_argument("input_path", help="Original ingest input to remove")
    parser.add_argument(
        "--archive", dest="archives", action="append", required=True,
        help="Archive path; supply both raw/originals/... and raw/sources/...",
    )
    parser.add_argument(
        "--confirm", action="store_true",
        help="Actually unlink the verified input (the default is a dry run)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the action without deleting, even when --confirm is present",
    )
    parser.add_argument("--root", help="Repository root (default: this repository)")
    return parser


def resolve_repo_path(raw_path: str) -> Path:
    """Return a lexical repository path without resolving symlinks."""
    path = Path(raw_path).expanduser()
    candidate = path if path.is_absolute() else PATHS.root / path
    resolved = Path(os.path.abspath(candidate))
    if not resolved.is_relative_to(PATHS.root):
        raise ValueError(f"path is outside repo: {resolved}")
    return resolved


def has_symlink_component(path: Path) -> bool:
    """Reject a symlink at the path itself or anywhere below the repo root."""
    relative = path.relative_to(PATHS.root)
    current = PATHS.root
    for component in relative.parts:
        current /= component
        if current.is_symlink():
            return True
    return False


def is_allowed_input_location(input_path: Path) -> bool:
    if input_path.is_relative_to(PATHS.raw_inbox):
        return True
    return input_path.parent == PATHS.root and input_path.name not in PROTECTED_ROOT_FILES and not input_path.name.startswith(".")


def validate_input(input_path: Path) -> None:
    if has_symlink_component(input_path):
        raise ValueError(f"refuse symlink input: {input_path}")
    if not input_path.exists():
        raise ValueError(f"input not found: {input_path}")
    if input_path.is_dir():
        raise ValueError(f"refuse to delete directory: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"input is not a regular file: {input_path}")
    if any(input_path.is_relative_to(directory) for directory in protected_dirs()):
        # raw/inbox is handled by the allowlist below; all other raw paths remain protected.
        if not input_path.is_relative_to(PATHS.raw_inbox):
            raise ValueError(f"refuse protected path: {input_path}")
    if not is_allowed_input_location(input_path):
        raise ValueError("input must be an explicit file in raw/inbox or the repository root")
    if input_path.suffix.lower() not in INPUT_SUFFIXES:
        raise ValueError(f"input type is not supported for ingest cleanup: {input_path.suffix or '(none)'}")


def validate_archives(input_path: Path, archives: list[Path]) -> None:
    if len(archives) < 2:
        raise ValueError("provide both an originals archive and a canonical sources archive")
    originals: list[Path] = []
    sources: list[Path] = []
    for archive in archives:
        if has_symlink_component(archive):
            raise ValueError(f"refuse symlink archive: {archive}")
        if not archive.exists():
            raise ValueError(f"missing archive target: {archive}")
        if archive.is_dir() or not archive.is_file():
            raise ValueError(f"archive must be a regular file: {archive}")
        if archive.is_relative_to(PATHS.raw_originals):
            originals.append(archive)
        elif archive.is_relative_to(PATHS.raw_sources):
            sources.append(archive)
        else:
            raise ValueError("archive must be below raw/originals or raw/sources: " + str(archive))

    if not originals:
        raise ValueError("missing raw/originals archive")
    if not sources:
        raise ValueError("missing raw/sources canonical archive")
    if not any(sha256_file(original) == sha256_file(input_path) for original in originals):
        raise ValueError("no raw/originals archive is byte-identical to the input (SHA-256 mismatch)")


def cleanup_input(input_path: Path, *, confirmed: bool, dry_run: bool = False) -> None:
    if dry_run or not confirmed:
        reason = "--dry-run" if dry_run else "--confirm is required"
        print(f"dry-run: would delete {PATHS.relative(input_path)} ({reason})")
        return
    input_path.unlink()
    print(f"deleted {PATHS.relative(input_path)}")


def main() -> int:
    args = build_parser().parse_args()
    if args.root:
        configure(args.root)
    try:
        input_path = resolve_repo_path(args.input_path)
        archives = [resolve_repo_path(path) for path in args.archives]
        validate_input(input_path)
        validate_archives(input_path, archives)
    except ValueError as error:
        print(f"ingest-cleanup: {error}", file=sys.stderr)
        return 1
    cleanup_input(input_path, confirmed=args.confirm, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
