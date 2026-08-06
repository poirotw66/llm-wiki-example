"""Tests for docling-pdf --engine fast|docling defaults."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location("docling_pdf", SCRIPTS / "docling-pdf.py")
assert SPEC and SPEC.loader
docling_pdf = importlib.util.module_from_spec(SPEC)
sys.modules["docling_pdf"] = docling_pdf
SPEC.loader.exec_module(docling_pdf)


def test_default_engine_is_fast() -> None:
    args = docling_pdf.build_parser().parse_args(["sample.pdf"])
    assert args.engine == docling_pdf.ENGINE_FAST


def test_engine_docling_is_selectable() -> None:
    args = docling_pdf.build_parser().parse_args(
        ["sample.pdf", "--engine", "docling"]
    )
    assert args.engine == docling_pdf.ENGINE_DOCLING
