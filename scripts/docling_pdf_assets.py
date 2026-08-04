"""Pure helpers for Docling vision-asset selection (no Docling import)."""

from __future__ import annotations

from typing import Any


def images_scale_for_dpi(dpi: int) -> float:
    """Map export DPI to Docling images_scale (72 DPI baseline)."""
    return max(dpi, 72) / 72.0


def pick_best_image(images: list[Any], min_area: int) -> Any | None:
    """Return the largest PIL image whose width*height >= min_area."""
    usable: list[tuple[int, Any]] = []
    for image in images:
        width, height = image.size
        area = width * height
        if area >= min_area:
            usable.append((area, image))
    if not usable:
        return None
    usable.sort(key=lambda item: item[0], reverse=True)
    return usable[0][1]
