"""Tests for SHA-256 ingest cache."""
from __future__ import annotations

import contextlib
import importlib.util
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load():
    path = SCRIPTS / "ingest-cache.py"
    spec = importlib.util.spec_from_file_location("ingest_cache", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["ingest_cache"] = module
    spec.loader.exec_module(module)
    return module


def test_lookup_miss_then_record_hit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    source = tmp_path / "doc.pdf"
    source.write_bytes(b"%PDF-demo")
    (tmp_path / "raw" / "sources").mkdir(parents=True)
    (tmp_path / "raw" / "sources" / "doc.md").write_text("# doc\n", encoding="utf-8")
    (tmp_path / "wiki" / "sources").mkdir(parents=True)
    (tmp_path / "wiki" / "sources" / "doc.md").write_text("# doc\n", encoding="utf-8")
    cache_path = tmp_path / "cache.json"
    module.DEFAULT_CACHE = cache_path

    lookup_args = SimpleNamespace(
        path=str(source),
        cache=str(cache_path),
        force=False,
        require_miss=False,
    )
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        assert module.cmd_lookup(lookup_args) == 0
    assert json.loads(buf.getvalue())["hit"] is False

    record_args = SimpleNamespace(
        path=str(source),
        cache=str(cache_path),
        archive_slug="doc",
        source_page="wiki/sources/doc.md",
    )
    assert module.cmd_record(record_args) == 0

    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        assert module.cmd_lookup(lookup_args) == 0
    payload = json.loads(buf.getvalue())
    assert payload["hit"] is True
    assert payload["entry"]["archive_slug"] == "doc"


def test_record_accepts_lookup_digest_after_cleanup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    source = tmp_path / "inbox.md"
    source.write_bytes(b"original")
    digest = module.sha256_file(source)
    (tmp_path / "raw/sources").mkdir(parents=True)
    (tmp_path / "raw/sources/doc.md").write_text("# doc\n", encoding="utf-8")
    (tmp_path / "wiki/sources").mkdir(parents=True)
    (tmp_path / "wiki/sources/doc.md").write_text("# doc\n", encoding="utf-8")
    source.unlink()
    args = SimpleNamespace(path=None, cache=str(tmp_path / "cache.json"), archive_slug="doc", source_page="wiki/sources/doc.md", sha256=digest, original_name="inbox.md", analysis_receipt="a" * 64, analysis_version="1", analysis_source_sha256="b" * 64, analysis_generated_by="agent/test", analysis_generated_at="2026-08-07T00:00:00Z")
    assert module.cmd_record(args) == 0
    entry = module.load_cache(tmp_path / "cache.json")["entries"][digest]
    assert entry["original_name"] == "inbox.md"
    assert entry["analysis_receipt"]["sha256"] == "a" * 64


def test_force_lookup_is_miss_even_when_cached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    source = tmp_path / "doc.pdf"
    source.write_bytes(b"abc")
    (tmp_path / "raw/sources").mkdir(parents=True)
    (tmp_path / "raw/sources/doc.md").write_text("x", encoding="utf-8")
    (tmp_path / "wiki/sources").mkdir(parents=True)
    (tmp_path / "wiki/sources/doc.md").write_text("x", encoding="utf-8")
    cache_path = tmp_path / "cache.json"
    cache_path.write_text(
        json.dumps(
            {
                "version": 1,
                "entries": {
                    module.sha256_file(source): {
                        "archive_slug": "doc",
                        "source_page": "wiki/sources/doc.md",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    args = SimpleNamespace(
        path=str(source),
        cache=str(cache_path),
        force=True,
        require_miss=False,
    )
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        assert module.cmd_lookup(args) == 0
    assert json.loads(buf.getvalue())["hit"] is False


def test_parallel_records_preserve_every_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    (tmp_path / "raw/sources").mkdir(parents=True)
    (tmp_path / "wiki/sources").mkdir(parents=True)
    cache_path = tmp_path / "cache.json"
    def record(number: int) -> int:
        slug = f"doc-{number}"
        (tmp_path / "raw/sources" / f"{slug}.md").write_text("# archive\n", encoding="utf-8")
        (tmp_path / "wiki/sources" / f"{slug}.md").write_text("# source\n", encoding="utf-8")
        return module.cmd_record(SimpleNamespace(path=None, cache=str(cache_path), archive_slug=slug, source_page=f"wiki/sources/{slug}.md", sha256=f"{number:064x}", original_name=f"{slug}.md", analysis_receipt=None, analysis_version="1"))
    with ThreadPoolExecutor(max_workers=8) as executor:
        assert list(executor.map(record, range(1, 9))) == [0] * 8
    assert len(module.load_cache(cache_path)["entries"]) == 8
