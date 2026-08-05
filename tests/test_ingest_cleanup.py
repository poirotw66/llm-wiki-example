"""Regression tests for the deliberately narrow ingest cleanup boundary."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "ingest-cleanup.py"
SPEC = importlib.util.spec_from_file_location("ingest_cleanup", SCRIPT)
assert SPEC and SPEC.loader
cleanup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cleanup)


def can_create_symlink(directory: Path) -> bool:
    """Return True when the host allows creating a file symlink in directory.

    Unprivileged Windows often raises WinError 1314 (privilege not held).
    """
    if not hasattr(os, "symlink"):
        return False
    source = directory / "_symlink_probe_src"
    link = directory / "_symlink_probe_link"
    source.write_text("probe", encoding="utf-8")
    try:
        link.symlink_to(source)
    except OSError:
        return False
    finally:
        if link.exists() or link.is_symlink():
            link.unlink()
        if source.exists():
            source.unlink()
    return True


def require_symlink_support(directory: Path) -> None:
    if not can_create_symlink(directory):
        pytest.skip("symlink creation unavailable (common on unprivileged Windows)")


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for directory in ("raw/inbox", "raw/originals", "raw/sources", "scripts", "wiki", "docs", "config"):
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cleanup, "ROOT", tmp_path)
    monkeypatch.setattr(cleanup, "INBOX_DIR", tmp_path / "raw/inbox")
    monkeypatch.setattr(cleanup, "ORIGINALS_DIR", tmp_path / "raw/originals")
    monkeypatch.setattr(cleanup, "SOURCES_DIR", tmp_path / "raw/sources")
    monkeypatch.setattr(cleanup, "PROTECTED_DIRS", tuple(tmp_path / part for part in (".git", "config", "docs", "raw", "scripts", "skills", "tests", "wiki")))
    return tmp_path


def archived_input(repo: Path, name: str = "brief.md") -> tuple[Path, Path, Path]:
    input_path = repo / "raw/inbox" / name
    input_path.write_bytes(b"immutable original")
    original = repo / "raw/originals" / name
    original.write_bytes(input_path.read_bytes())
    canonical = repo / "raw/sources" / "brief.md"
    canonical.write_text("# Canonical archive\n", encoding="utf-8")
    return input_path, original, canonical


def test_default_is_dry_run_after_valid_archive_contract(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_path, original, canonical = archived_input(repo)
    cleanup.validate_input(input_path)
    cleanup.validate_archives(input_path, [original, canonical])

    cleanup.cleanup_input(input_path, confirmed=False)

    assert input_path.exists()
    assert "--confirm is required" in capsys.readouterr().out


def test_confirmed_cleanup_deletes_only_verified_input(repo: Path) -> None:
    input_path, original, canonical = archived_input(repo)
    cleanup.validate_input(input_path)
    cleanup.validate_archives(input_path, [original, canonical])

    cleanup.cleanup_input(input_path, confirmed=True)

    assert not input_path.exists()
    assert original.exists()
    assert canonical.exists()


@pytest.mark.parametrize("bad_path", ["scripts/wiki-lint.py", "wiki/index.md", "docs/guide.md", "config/cleanup.md"])
def test_refuses_previously_deletable_protected_paths(repo: Path, bad_path: str) -> None:
    target = repo / bad_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("do not remove", encoding="utf-8")

    with pytest.raises(ValueError, match="protected path|raw/inbox or the repository root"):
        cleanup.validate_input(target)


def test_requires_both_archive_roles_and_identical_original(repo: Path) -> None:
    input_path, original, canonical = archived_input(repo)

    with pytest.raises(ValueError, match="both an originals archive"):
        cleanup.validate_archives(input_path, [original])

    original.write_bytes(b"different")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        cleanup.validate_archives(input_path, [original, canonical])


def test_refuses_symlink_input_and_archive(repo: Path) -> None:
    require_symlink_support(repo / "raw/inbox")
    input_path, original, canonical = archived_input(repo)
    linked_input = repo / "raw/inbox" / "linked.md"
    linked_input.symlink_to(input_path)
    with pytest.raises(ValueError, match="symlink input"):
        cleanup.validate_input(linked_input)

    linked_archive = repo / "raw/originals" / "linked.md"
    linked_archive.symlink_to(original)
    with pytest.raises(ValueError, match="symlink archive"):
        cleanup.validate_archives(input_path, [linked_archive, canonical])


def test_refuses_root_repository_files_and_unsupported_types(repo: Path) -> None:
    readme = repo / "README.md"
    readme.write_text("protected", encoding="utf-8")
    with pytest.raises(ValueError, match="raw/inbox or the repository root"):
        cleanup.validate_input(readme)

    executable = repo / "upload.py"
    executable.write_text("print('not an ingest artifact')", encoding="utf-8")
    with pytest.raises(ValueError, match="not supported"):
        cleanup.validate_input(executable)


def test_rejects_paths_outside_the_repository(repo: Path) -> None:
    with pytest.raises(ValueError, match="outside repo"):
        cleanup.resolve_repo_path(str(repo.parent / "outside.md"))
