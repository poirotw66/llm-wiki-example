#!/usr/bin/env python3
"""Docling-first PDF draft + page triage for the vision gate.

Default path: Docling → structured Markdown draft.
Vision path: only pages flagged by triage (short text layer and/or diagram cues).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Fixed Docling artifacts dir (contains RapidOcr/). Override with DOCLING_ARTIFACTS_PATH.
DEFAULT_DOCLING_ARTIFACTS = ROOT / "models" / "docling"
DEFAULT_CHAR_THRESHOLD = 200
DEFAULT_IMAGE_AREA = 80_000
VISION_KEYWORDS = (
    "架構圖",
    "架構",
    "流程圖",
    "對照表",
    "對照",
    "狀態機",
    "生命週期",
    "儀表板",
    "Before / After",
    "Before/After",
    "architecture",
    "flowchart",
    "diagram",
)


@dataclass(frozen=True)
class PageTriage:
    page: int
    char_count: int
    reasons: list[str]
    needs_vision: bool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert PDF with Docling and triage pages for vision."
    )
    parser.add_argument("pdf", help="PDF path (repo-relative or absolute)")
    parser.add_argument(
        "--base-slug",
        help="Asset slug; default = PDF stem",
    )
    parser.add_argument(
        "--out",
        help="Draft Markdown output path; default = /tmp/<base-slug>-docling-draft.md",
    )
    parser.add_argument("--page-from", type=int, default=1, help="First page (1-based)")
    parser.add_argument("--page-to", type=int, default=0, help="Last page; 0 = last page")
    parser.add_argument(
        "--char-threshold",
        type=int,
        default=DEFAULT_CHAR_THRESHOLD,
        help="Pages with fewer chars are vision candidates",
    )
    parser.add_argument(
        "--image-area",
        type=int,
        default=DEFAULT_IMAGE_AREA,
        help="Min width*height of embedded image to flag page",
    )
    parser.add_argument(
        "--triage-only",
        action="store_true",
        help="Skip Docling; only print page triage JSON",
    )
    parser.add_argument(
        "--export-vision-assets",
        action="store_true",
        help="pdftoppm only vision-flagged pages into raw/assets/<base-slug>/",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=144,
        help="DPI for vision asset export (default 144)",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Fail if Docling is unavailable (default: fall back to pdftotext)",
    )
    return parser


def resolve_path(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def require_cmd(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"missing command: {name}")
    return path


def pdf_page_count(pdf: Path) -> int:
    out = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    match = re.search(r"^Pages:\s+(\d+)", out, re.MULTILINE)
    if not match:
        raise RuntimeError("pdfinfo: could not read page count")
    return int(match.group(1))


def page_text(pdf: Path, page: int) -> str:
    return subprocess.check_output(
        ["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
        text=True,
        errors="replace",
    )


def embedded_image_pages(pdf: Path, min_area: int) -> dict[int, int]:
    """Return {page: max_image_area} for pages with large embedded images."""
    if not shutil.which("pdfimages"):
        return {}
    out = subprocess.check_output(["pdfimages", "-list", str(pdf)], text=True)
    areas: dict[int, int] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 5 or not parts[0].isdigit():
            continue
        page = int(parts[0])
        try:
            width = int(parts[3])
            height = int(parts[4])
        except ValueError:
            continue
        area = width * height
        if area >= min_area:
            areas[page] = max(areas.get(page, 0), area)
    return areas


def triage_page(
    page: int,
    text: str,
    char_threshold: int,
    image_area: int | None,
) -> PageTriage:
    compact = re.sub(r"\s+", "", text)
    reasons: list[str] = []
    short = len(compact) < char_threshold
    if short:
        reasons.append(f"short_text<{char_threshold}")
    if image_area is not None:
        reasons.append(f"large_image_area={image_area}")
    hits = [kw for kw in VISION_KEYWORDS if kw.lower() in text.lower()]
    # Keyword alone on long TOC pages is often a false positive.
    if hits and (short or image_area is not None or len(compact) < char_threshold * 4):
        reasons.append("keyword:" + ",".join(hits[:5]))
    needs_vision = short or image_area is not None or (
        bool(hits) and len(compact) < char_threshold * 4
    )
    return PageTriage(
        page=page,
        char_count=len(compact),
        reasons=reasons,
        needs_vision=needs_vision,
    )


def triage_pdf(
    pdf: Path,
    page_from: int,
    page_to: int,
    char_threshold: int,
    min_image_area: int,
) -> list[PageTriage]:
    image_pages = embedded_image_pages(pdf, min_image_area)
    return [
        triage_page(
            page,
            page_text(pdf, page),
            char_threshold,
            image_pages.get(page),
        )
        for page in range(page_from, page_to + 1)
    ]


def resolve_docling_artifacts() -> Path:
    """Return artifacts_path parent that must contain RapidOcr/."""
    import os

    raw = os.environ.get("DOCLING_ARTIFACTS_PATH")
    if raw:
        return Path(raw).expanduser().resolve()
    return DEFAULT_DOCLING_ARTIFACTS.resolve()


def convert_with_docling(pdf: Path, page_from: int, page_to: int) -> str:
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError as error:
        raise RuntimeError(
            "docling is not installed; run: uv sync --group pdf"
        ) from error

    artifacts = resolve_docling_artifacts()
    rapidocr_dir = artifacts / "RapidOcr"
    if not rapidocr_dir.is_dir():
        raise RuntimeError(
            f"Docling RapidOCR models missing at {rapidocr_dir}. "
            "Download once with: "
            f"uv run docling-tools models download rapidocr -o {artifacts}"
        )

    try:
        pipeline_options = PdfPipelineOptions(artifacts_path=str(artifacts))
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = converter.convert(str(pdf), page_range=(page_from, page_to))
        return result.document.export_to_markdown()
    except Exception as error:
        # Common on machines with torch < 2.4: layout models fail to import.
        raise RuntimeError(
            "Docling convert failed. Install PDF deps with: "
            "uv sync --group pdf "
            "(Intel Mac pins torch==2.2.2, numpy<2, transformers<5; "
            "elsewhere torch>=2.4). "
            f"Original error: {error}"
        ) from error


def convert_with_pdftotext_fallback(
    pdf: Path, page_from: int, page_to: int
) -> str:
    """Build a crude per-page Markdown draft when Docling is unavailable."""
    sections: list[str] = []
    for page in range(page_from, page_to + 1):
        text = page_text(pdf, page).strip() or "（此頁文字層為空）"
        sections.append(f"### 第 {page} 頁\n\n{text}\n")
    return "\n".join(sections)


def pad_page(page: int, total_pages: int) -> str:
    width = 3 if total_pages >= 100 else 2
    return f"{page:0{width}d}"


def export_vision_assets(
    pdf: Path,
    base_slug: str,
    pages: list[int],
    total_pages: int,
    dpi: int,
) -> list[Path]:
    if not pages:
        return []
    require_cmd("pdftoppm")
    asset_dir = ROOT / "raw" / "assets" / base_slug
    asset_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for page in pages:
        prefix = Path("/tmp") / f"{base_slug}-vision-{page}"
        subprocess.check_call(
            [
                "pdftoppm",
                "-f",
                str(page),
                "-l",
                str(page),
                "-png",
                "-r",
                str(dpi),
                str(pdf),
                str(prefix),
            ]
        )
        produced = sorted(prefix.parent.glob(f"{prefix.name}-*.png"))
        if not produced:
            raise RuntimeError(f"pdftoppm produced no file for page {page}")
        target = asset_dir / f"p{pad_page(page, total_pages)}.png"
        shutil.move(str(produced[0]), target)
        written.append(target)
    return written


def wrap_draft(
    markdown: str,
    *,
    base_slug: str,
    pdf: Path,
    page_from: int,
    page_to: int,
    triage: list[PageTriage],
    engine: str,
) -> str:
    vision_pages = [item.page for item in triage if item.needs_vision]
    draft_heading = (
        "## Docling 初稿" if engine == "docling" else "## 文字層初稿（Docling 後備）"
    )
    meta = "\n".join(
        [
            "## 來源資訊",
            "",
            f"- base-slug：`{base_slug}`",
            f"- 原件：`{pdf}`",
            f"- 頁面範圍：第 {page_from}–{page_to} 頁",
            f"- 轉檔引擎：`{engine}`",
            f"- 視覺閘候選頁：{vision_pages or '無'}",
            "- 說明：文字／表格足夠之頁可直接整理進 `raw/sources/`；"
            "候選頁須 `pdftoppm` + vision／VLM 補 Visual Evidence"
            "（見 docs/pdf-ingest-sop.md）。",
            "",
            "---",
            "",
            draft_heading,
            "",
            markdown.strip(),
            "",
        ]
    )
    return meta


def main() -> int:
    args = build_parser().parse_args()
    try:
        require_cmd("pdfinfo")
        require_cmd("pdftotext")
        pdf = resolve_path(args.pdf)
        if not pdf.is_file():
            raise RuntimeError(f"PDF not found: {pdf}")

        total_pages = pdf_page_count(pdf)
        page_from = max(1, args.page_from)
        page_to = total_pages if args.page_to <= 0 else min(args.page_to, total_pages)
        if page_from > page_to:
            raise RuntimeError(f"invalid page range: {page_from}-{page_to}")

        base_slug = args.base_slug or pdf.stem
        triage = triage_pdf(
            pdf, page_from, page_to, args.char_threshold, args.image_area
        )
        vision_pages = [item.page for item in triage if item.needs_vision]

        summary = {
            "pdf": str(pdf.relative_to(ROOT)) if pdf.is_relative_to(ROOT) else str(pdf),
            "base_slug": base_slug,
            "page_from": page_from,
            "page_to": page_to,
            "char_threshold": args.char_threshold,
            "image_area": args.image_area,
            "vision_pages": vision_pages,
            "triage": [asdict(item) for item in triage],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

        if args.export_vision_assets:
            written = export_vision_assets(
                pdf, base_slug, vision_pages, total_pages, args.dpi
            )
            print(
                json.dumps(
                    {"exported_assets": [str(path.relative_to(ROOT)) for path in written]},
                    ensure_ascii=False,
                    indent=2,
                )
            )

        if args.triage_only:
            return 0

        engine = "docling"
        try:
            markdown = convert_with_docling(pdf, page_from, page_to)
        except RuntimeError as error:
            if args.no_fallback:
                raise
            print(
                f"docling-pdf: Docling unavailable, fallback to pdftotext ({error})",
                file=sys.stderr,
            )
            markdown = convert_with_pdftotext_fallback(pdf, page_from, page_to)
            engine = "pdftotext-fallback"

        out = (
            resolve_path(args.out)
            if args.out
            else Path(f"/tmp/{base_slug}-docling-draft.md")
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            wrap_draft(
                markdown,
                base_slug=base_slug,
                pdf=pdf,
                page_from=page_from,
                page_to=page_to,
                triage=triage,
                engine=engine,
            ),
            encoding="utf-8",
        )
        print(json.dumps({"draft": str(out), "engine": engine}, ensure_ascii=False))
        return 0
    except RuntimeError as error:
        print(f"docling-pdf: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"docling-pdf: command failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
