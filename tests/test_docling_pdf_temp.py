"""Tests for portable OS temp paths in docling-pdf."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location("docling_pdf", SCRIPTS / "docling-pdf.py")
assert SPEC and SPEC.loader
docling_pdf = importlib.util.module_from_spec(SPEC)
sys.modules["docling_pdf"] = docling_pdf
SPEC.loader.exec_module(docling_pdf)


def test_os_temp_dir_uses_tempfile_gettempdir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(docling_pdf.tempfile, "gettempdir", lambda: str(tmp_path))
    assert docling_pdf.os_temp_dir() == tmp_path


def test_temp_path_joins_under_os_temp(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(docling_pdf.tempfile, "gettempdir", lambda: str(tmp_path))
    target = docling_pdf.temp_path("demo-vision-1")
    assert target == tmp_path / "demo-vision-1"
    assert target.parent == tmp_path
