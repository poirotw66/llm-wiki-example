"""Tests for the helpers shared by scripts/ and for the invariants they protect."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:  # Mirrors the bootstrap each script performs.
    sys.path.append(str(SCRIPTS))

import _common


def _load(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _path_constants(module) -> list[str]:
    return [
        name
        for name, value in vars(module).items()
        if isinstance(value, Path) and name != "ROOT" and not name.startswith("_")
    ]


def test_every_bundle_location_derives_from_the_root(tmp_path: Path) -> None:
    paths = _common.Paths(tmp_path)
    locations = [
        name for name, value in vars(_common.Paths).items() if isinstance(value, property)
    ]
    assert locations, "Paths exposes no locations; the reflection below proves nothing"
    for name in locations:
        assert getattr(paths, name).is_relative_to(tmp_path), name


def test_lint_keeps_no_path_constants_outside_the_configured_root() -> None:
    """A module-level ``ROOT / ...`` constant would survive ``configure`` and
    silently read the real repository during tests."""
    module = _load("wiki-lint.py", "wiki_lint_paths")
    assert _path_constants(module) == []


def test_graph_insights_keeps_no_path_constants_outside_the_configured_root() -> None:
    module = _load("wiki-graph-insights.py", "wiki_graph_insights_paths")
    assert _path_constants(module) == []


def test_lint_and_usage_share_one_log_grammar() -> None:
    """wiki-lint enforces the log format and wiki-usage attributes tokens from
    it; separate copies can drift into lint-clean but unattributable logs."""
    lint = _load("wiki-lint.py", "wiki_lint_grammar")
    usage = _load("wiki-usage.py", "wiki_usage_grammar")
    assert lint.LOG_OPERATION is _common.LOG_OPERATION
    assert usage.LOG_OPERATION is _common.LOG_OPERATION
    assert lint.LOG_DATE is _common.LOG_DATE
    assert usage.LOG_DATE is _common.LOG_DATE


def test_log_grammar_accepts_documented_entries_and_rejects_others() -> None:
    assert _common.LOG_DATE.fullmatch("## 2026-08-13")
    assert not _common.LOG_DATE.fullmatch("## 13-08-2026")
    entry = _common.LOG_OPERATION.fullmatch("- **ingest** | 某規格.pdf")
    assert entry and entry.group("operation") == "ingest"
    assert entry.group("title") == "某規格.pdf"
    assert not _common.LOG_OPERATION.fullmatch("- **deploy** | not an operation")
    bracket = _common.LOG_BRACKET_OPERATION.fullmatch("## [2026-08-13] lint | 品質檢查")
    assert bracket and bracket.group("date") == "2026-08-13"


def test_display_falls_back_to_the_absolute_path(tmp_path: Path) -> None:
    paths = _common.Paths(tmp_path / "bundle")
    inside = tmp_path / "bundle" / "ops" / "graph-insights.md"
    outside = tmp_path / "elsewhere" / "graph-insights.md"
    assert paths.display(inside) == str(Path("ops") / "graph-insights.md")
    assert paths.display(outside) == str(outside)


def test_wiki_pages_skips_reserved_files(tmp_path: Path) -> None:
    paths = _common.Paths(tmp_path)
    (paths.wiki / "concepts").mkdir(parents=True)
    for name in ("index.md", "log.md"):
        (paths.wiki / name).write_text("# reserved\n", encoding="utf-8")
    page = paths.wiki / "concepts" / "api.md"
    page.write_text("# API\n", encoding="utf-8")
    assert paths.wiki_pages() == [page]


def test_wiki_pages_tolerates_a_missing_bundle(tmp_path: Path) -> None:
    assert _common.Paths(tmp_path).wiki_pages() == []


def test_sha256_file_matches_hashlib(tmp_path: Path) -> None:
    target = tmp_path / "archive.md"
    payload = b"visual evidence\n" * 100_000
    target.write_bytes(payload)
    assert _common.sha256_file(target) == hashlib.sha256(payload).hexdigest()


def test_atomic_write_creates_parents_and_replaces(tmp_path: Path) -> None:
    target = tmp_path / "ops" / "queue.md"
    _common.atomic_write(target, "first\n")
    assert target.read_text(encoding="utf-8") == "first\n"
    _common.atomic_write(target, "second\n")
    assert target.read_text(encoding="utf-8") == "second\n"
    assert list(target.parent.iterdir()) == [target], "temporary file left behind"


def test_git_output_returns_none_when_git_fails(tmp_path: Path) -> None:
    assert _common.git_output("rev-parse", "definitely-not-a-revision") is None
    assert _common.git("rev-parse", "--show-toplevel", cwd=_common.ROOT).strip()
