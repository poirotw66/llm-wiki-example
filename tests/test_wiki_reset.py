"""Tests for wiki-reset blank-template helper."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "wiki-reset.py"
SPEC = importlib.util.spec_from_file_location("wiki_reset", SCRIPT)
assert SPEC and SPEC.loader
wiki_reset = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wiki_reset)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    wiki = tmp_path / "wiki"
    raw = tmp_path / "raw"
    for relative in (
        "wiki/sources",
        "wiki/concepts",
        "wiki/entities",
        "wiki/queries",
        "wiki/faq",
        "wiki/graph",
        "wiki/lint",
        "raw/inbox",
        "raw/originals",
        "raw/sources",
        "raw/assets",
    ):
        (tmp_path / relative).mkdir(parents=True, exist_ok=True)
        (tmp_path / relative / ".gitkeep").write_text("", encoding="utf-8")

    (wiki / "index.md").write_text("# old index\n", encoding="utf-8")
    (wiki / "log.md").write_text("# Wiki Log\n\n## 2026-01-01\n\n- **lint** | seed\n", encoding="utf-8")
    (tmp_path / "ops").mkdir()
    (tmp_path / "ops" / "purpose.md").write_text("# keep\n", encoding="utf-8")
    (wiki / "lint" / "report.md").write_text("# lint keep\n", encoding="utf-8")
    (wiki / "sources" / "demo.md").write_text("# source\n", encoding="utf-8")
    (wiki / "concepts" / "idea.md").write_text("# concept\n", encoding="utf-8")
    (raw / "originals" / "demo.pdf").write_bytes(b"%PDF")
    (raw / "sources" / "demo.md").write_text("# archive\n", encoding="utf-8")
    assets = raw / "assets" / "demo"
    assets.mkdir()
    (assets / "p01.png").write_bytes(b"png")

    # One call: the knowledge and raw directory sets follow the root, so a
    # directory added to the script is covered here without editing this.
    wiki_reset.configure(tmp_path)
    return tmp_path


def test_dry_run_does_not_delete(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = wiki_reset.reset_wiki(confirmed=False, skip_log=False)
    assert code == 0
    assert (repo / "wiki/sources/demo.md").exists()
    assert (repo / "raw/originals/demo.pdf").exists()
    assert "--confirm is required" in capsys.readouterr().out


def test_every_configured_directory_is_cleared(repo: Path) -> None:
    """Derived from the script's own lists, so a directory added there is
    covered here without editing this test."""
    assert wiki_reset.KNOWLEDGE_DIR_NAMES and wiki_reset.RAW_CONTENT_DIR_NAMES
    seeded = []
    for parent, names in (
        ("wiki", wiki_reset.KNOWLEDGE_DIR_NAMES),
        ("raw", wiki_reset.RAW_CONTENT_DIR_NAMES),
    ):
        for name in names:
            item = repo / parent / name / "item.md"
            item.parent.mkdir(parents=True, exist_ok=True)
            item.write_text("# seeded\n", encoding="utf-8")
            seeded.append(item)

    assert wiki_reset.reset_wiki(confirmed=True, skip_log=True) == 0

    for item in seeded:
        assert not item.exists(), item
        assert (item.parent / ".gitkeep").exists(), item.parent
    assert (repo / "wiki/lint/report.md").exists(), "wiki/lint/ must be preserved"


def test_confirm_resets_knowledge_and_raw_keeps_lint(repo: Path) -> None:
    code = wiki_reset.reset_wiki(confirmed=True, skip_log=False)
    assert code == 0
    assert not (repo / "wiki/sources/demo.md").exists()
    assert not (repo / "wiki/concepts/idea.md").exists()
    assert not (repo / "raw/originals/demo.pdf").exists()
    assert not (repo / "raw/assets/demo").exists()
    assert (repo / "wiki/lint/report.md").exists()
    assert (repo / "ops/purpose.md").read_text(encoding="utf-8") == "# keep\n"
    assert (repo / "ops/review-queue.md").is_file()
    index = (repo / "wiki/index.md").read_text(encoding="utf-8")
    assert 'okf_version: "0.2"' in index
    assert "刻意留白" in index
    assert (repo / "wiki/sources/.gitkeep").exists()
    assert (repo / "raw/originals/.gitkeep").exists()
    log = (repo / "wiki/log.md").read_text(encoding="utf-8")
    assert "初始化 wiki 回範本空白" in log
    assert "## 2026-01-01" in log
