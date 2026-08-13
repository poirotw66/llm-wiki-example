"""Tests for ingest-review queue helper."""
from __future__ import annotations

import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load():
    path = SCRIPTS / "ingest-review.py"
    spec = importlib.util.spec_from_file_location("ingest_review", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["ingest_review"] = module
    spec.loader.exec_module(module)
    return module


def test_append_and_close_review_item(tmp_path: Path) -> None:
    module = _load()
    module.configure(tmp_path)
    queue_path = module.PATHS.review_queue

    append_args = SimpleNamespace(
        queue=str(queue_path),
        title="Need human verify",
        reason="contradiction candidate",
        source="ingest",
        action="human_verify",
        related=["wiki/concepts/a.md"],
        id="abc123",
    )
    assert module.cmd_append(append_args) == 0
    text = queue_path.read_text(encoding="utf-8")
    assert "- [ ] id: abc123 |" in text
    assert "suggested_action: human_verify" in text

    close_args = SimpleNamespace(queue=str(queue_path), id="abc123")
    assert module.cmd_close(close_args) == 0
    text = queue_path.read_text(encoding="utf-8")
    assert "- [x] id: abc123 |" in text
    open_part, done_part = text.split("## Done", 1)
    assert "abc123" in done_part
    assert "- [ ] id: abc123 |" not in open_part


def test_parallel_appends_are_not_lost(tmp_path: Path) -> None:
    module = _load()
    module.configure(tmp_path)
    queue_path = module.PATHS.review_queue
    def append(number: int) -> int:
        return module.cmd_append(SimpleNamespace(queue=str(queue_path), title=f"title {number}", reason="test", source="ingest", action="human_verify", related=[], id=f"id{number}"))
    with ThreadPoolExecutor(max_workers=8) as executor:
        assert list(executor.map(append, range(8))) == [0] * 8
    text = queue_path.read_text(encoding="utf-8")
    assert sum(1 for number in range(8) if f"id: id{number} |" in text) == 8
