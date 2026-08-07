"""Tests for wiki-graph-insights structural report."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load():
    path = SCRIPTS / "wiki-graph-insights.py"
    spec = importlib.util.spec_from_file_location("wiki_graph_insights", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["wiki_graph_insights"] = module
    spec.loader.exec_module(module)
    return module


def test_insights_lists_missing_source_page(tmp_path: Path, monkeypatch) -> None:
    module = _load()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    wiki = tmp_path / "wiki"
    module.WIKI = wiki
    module.RAW_SOURCES = tmp_path / "raw" / "sources"
    (wiki / "concepts").mkdir(parents=True)
    module.RAW_SOURCES.mkdir(parents=True)
    (module.RAW_SOURCES / "orphan-archive.md").write_text("# raw\n", encoding="utf-8")
    (wiki / "concepts" / "a.md").write_text(
        "# A\n\nSee [Index](../index.md).\n",
        encoding="utf-8",
    )
    (wiki / "index.md").write_text("# Index\n", encoding="utf-8")
    out = wiki / "graph" / "insights.md"
    assert module.main(["--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "orphan-archive.md" in text
    assert "Isolated pages" in text
