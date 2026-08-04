"""Tests for Docling vision-asset selection helpers."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from docling_pdf_assets import images_scale_for_dpi, pick_best_image


def test_pick_best_image_returns_largest_above_min_area() -> None:
    small = Image.new("RGB", (100, 100), color="red")
    medium = Image.new("RGB", (400, 300), color="green")
    large = Image.new("RGB", (800, 600), color="blue")

    chosen = pick_best_image([small, large, medium], min_area=80_000)

    assert chosen is large


def test_pick_best_image_returns_none_when_all_below_min_area() -> None:
    tiny = Image.new("RGB", (50, 50), color="red")

    chosen = pick_best_image([tiny], min_area=80_000)

    assert chosen is None


def test_images_scale_for_dpi_uses_72_baseline() -> None:
    assert images_scale_for_dpi(144) == 2.0
    assert images_scale_for_dpi(72) == 1.0
