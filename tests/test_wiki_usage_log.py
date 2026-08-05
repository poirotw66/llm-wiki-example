"""Tests for OKF v0.2 operation-log parsing."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_usage():
    path = Path(__file__).resolve().parents[1] / "scripts" / "wiki-usage.py"
    spec = importlib.util.spec_from_file_location("wiki_usage_log", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["wiki_usage_log"] = module
    spec.loader.exec_module(module)
    return module


def test_log_entries_reads_v02_date_groups(tmp_path: Path) -> None:
    module = _load_usage()
    log = tmp_path / "log.md"
    log.write_text(
        "# Wiki Log\n\n"
        "## 2026-08-05\n\n"
        "- **lint** | schema migration\n"
        "  - pass\n"
        "- **query** | smoke test\n"
        "  - no-op\n",
        encoding="utf-8",
    )

    entries = module.log_entries(log)

    assert [(entry["date"], entry["operation"], entry["title"]) for entry in entries] == [
        ("2026-08-05", "lint", "schema migration"),
        ("2026-08-05", "query", "smoke test"),
    ]
    assert module.status_from_log(entries[0]["body"]) == "pass"
    assert module.status_from_log(entries[1]["body"]) == "no-op"


def test_log_entries_ignores_non_v02_headings(tmp_path: Path) -> None:
    module = _load_usage()
    log = tmp_path / "log.md"
    log.write_text("# Wiki Log\n\n## [2026-08-04] lint | old\n\n- pass\n", encoding="utf-8")

    assert module.log_entries(log) == []
