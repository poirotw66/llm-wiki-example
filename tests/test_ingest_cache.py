"""Tests for SHA-256 ingest cache."""
from __future__ import annotations

import contextlib
import importlib.util
import json
import sys
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
