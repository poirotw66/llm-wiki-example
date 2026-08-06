#!/usr/bin/env python3
"""PDF draft + page triage for the vision gate.

Default engine ``fast``: pdftotext draft + triage + pdftoppm for vision pages.
Optional engine ``docling``: Docling structured Markdown (+ optional picture crop).

Vision path: only pages flagged by triage (short text layer and/or diagram cues).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from docling_pdf_assets import images_scale_for_dpi, pick_best_image

ROOT = Path(__file__).resolve().parents[1]


def os_temp_dir() -> Path:
    """Return the OS temp directory (portable; do not hard-code /tmp)."""
    return Path(tempfile.gettempdir())


def temp_path(name: str) -> Path:
    """Build a path under the OS temp directory."""
    return os_temp_dir() / name


# Fixed Docling artifacts dir (contains RapidOcr/). Override with DOCLING_ARTIFACTS_PATH.
DEFAULT_DOCLING_ARTIFACTS = ROOT / "models" / "docling"
DEFAULT_CHAR_THRESHOLD = 200
DEFAULT_IMAGE_AREA = 80_000
ENGINE_FAST = "fast"
ENGINE_DOCLING = "docling"
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


@dataclass(frozen=True)
class ExportedAsset:
    path: Path
    page: int
    method: str
    width: int
    height: int


@dataclass(frozen=True)
class DoclingConvertResult:
    markdown: str
    document: Any | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert PDF to a Markdown draft and triage pages for vision. "
            "Default engine is fast (pdftotext); use --engine docling for full parse."
        )
    )
    parser.add_argument("pdf", help="PDF path (repo-relative or absolute)")
    parser.add_argument(
        "--base-slug",
        help="Asset slug; default = PDF stem",
    )
    parser.add_argument(
        "--out",
        help=(
            "Draft Markdown output path; "
            "default = <OS-temp>/<base-slug>-pdf-draft.md"
        ),
    )
    parser.add_argument(
        "--engine",
        choices=(ENGINE_FAST, ENGINE_DOCLING),
        default=ENGINE_FAST,
        help=(
            "Draft engine: fast = pdftotext + pdftoppm (default); "
            "docling = Docling structured MD (optional; needs models)"
        ),
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
        help="Min width*height of embedded image to flag page / accept as asset",
    )
    parser.add_argument(
        "--triage-only",
        action="store_true",
        help="Skip Markdown draft; Docling runs only when --engine docling exports pictures",
    )
    parser.add_argument(
        "--export-vision-assets",
        action="store_true",
        help=(
            "Export vision-flagged pages into raw/assets/<base-slug>/; "
            "fast engine uses pdftoppm; docling prefers pictures then pdftoppm"
        ),
    )
    parser.add_argument(
        "--force-page-render",
        action="store_true",
        help="Always use pdftoppm full-page render (skip Docling picture extract)",
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
        help="With --engine docling, fail if Docling is unavailable",
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


def picture_page_number(picture: Any) -> int | None:
    prov = getattr(picture, "prov", None) or []
    if not prov:
        return None
    page_no = getattr(prov[0], "page_no", None)
    return int(page_no) if page_no is not None else None


def collect_pictures_by_page(document: Any) -> dict[int, list[Any]]:
    """Map 1-based page → PIL images from Docling PictureItem nodes."""
    from docling_core.types.doc import PictureItem

    by_page: dict[int, list[Any]] = {}
    for item, _level in document.iterate_items():
        if not isinstance(item, PictureItem):
            continue
        page = picture_page_number(item)
        if page is None:
            continue
        image = item.get_image(document)
        if image is None:
            continue
        by_page.setdefault(page, []).append(image)
    return by_page


def convert_with_docling(
    pdf: Path,
    page_from: int,
    page_to: int,
    *,
    extract_images: bool = False,
    images_scale: float = 2.0,
) -> DoclingConvertResult:
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError as error:
        raise RuntimeError(
            "docling is not installed; run: uv sync --group pdf"
        ) from error

    artifacts = resolve_docling_artifacts()
    required = (
        artifacts / "RapidOcr",
        artifacts / "docling-project--docling-layout-heron",
        artifacts / "docling-project--docling-models",
    )
    missing = [str(path) for path in required if not path.is_dir()]
    if missing:
        listed = "\n".join(f" - {path}" for path in missing)
        raise RuntimeError(
            "Docling models missing under artifacts_path:\n"
            f"{listed}\n"
            "Download the default set once with:\n"
            f"  uv run docling-tools models download -o {artifacts}"
        )

    try:
        pipeline_options = PdfPipelineOptions(
            artifacts_path=str(artifacts),
            generate_picture_images=extract_images,
            generate_page_images=extract_images,
            images_scale=images_scale if extract_images else 1.0,
        )
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = converter.convert(str(pdf), page_range=(page_from, page_to))
        return DoclingConvertResult(
            markdown=result.document.export_to_markdown(),
            document=result.document if extract_images else None,
        )
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


def export_page_via_pdftoppm(
    pdf: Path,
    page: int,
    target: Path,
    dpi: int,
    base_slug: str,
) -> ExportedAsset:
    require_cmd("pdftoppm")
    prefix = temp_path(f"{base_slug}-vision-{page}")
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
    shutil.move(str(produced[0]), target)
    # Optional: read size via sips/file; keep zeros if unavailable.
    width = height = 0
    try:
        from PIL import Image

        with Image.open(target) as image:
            width, height = image.size
    except Exception:
        pass
    return ExportedAsset(
        path=target,
        page=page,
        method="pdftoppm_page",
        width=width,
        height=height,
    )


def export_vision_assets(
    pdf: Path,
    base_slug: str,
    pages: list[int],
    total_pages: int,
    dpi: int,
    *,
    min_image_area: int = DEFAULT_IMAGE_AREA,
    document: Any | None = None,
    force_page_render: bool = False,
    page_from: int | None = None,
    page_to: int | None = None,
) -> list[ExportedAsset]:
    """Export one PNG per vision page: Docling picture first, else full page."""
    if not pages:
        return []

    asset_dir = ROOT / "raw" / "assets" / base_slug
    asset_dir.mkdir(parents=True, exist_ok=True)

    pictures_by_page: dict[int, list[Any]] = {}
    if not force_page_render:
        doc = document
        if doc is None:
            convert_from = page_from if page_from is not None else min(pages)
            convert_to = page_to if page_to is not None else max(pages)
            try:
                converted = convert_with_docling(
                    pdf,
                    convert_from,
                    convert_to,
                    extract_images=True,
                    images_scale=images_scale_for_dpi(dpi),
                )
                doc = converted.document
            except RuntimeError as error:
                print(
                    f"docling-pdf: picture extract unavailable, "
                    f"using pdftoppm ({error})",
                    file=sys.stderr,
                )
                doc = None
        if doc is not None:
            pictures_by_page = collect_pictures_by_page(doc)

    written: list[ExportedAsset] = []
    for page in pages:
        target = asset_dir / f"p{pad_page(page, total_pages)}.png"
        best = None
        if not force_page_render:
            best = pick_best_image(pictures_by_page.get(page, []), min_image_area)
        if best is not None:
            best.save(target, format="PNG")
            width, height = best.size
            written.append(
                ExportedAsset(
                    path=target,
                    page=page,
                    method="docling_picture",
                    width=width,
                    height=height,
                )
            )
            continue
        written.append(
            export_page_via_pdftoppm(pdf, page, target, dpi, base_slug)
        )
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
    if engine == ENGINE_DOCLING:
        draft_heading = "## Docling 初稿"
        export_note = (
            "候選頁匯出資產時優先 Docling 內嵌／裁切圖，"
            "抽不到再用整頁 `pdftoppm`，並以 vision／VLM 補 Visual Evidence"
        )
    elif engine == "pdftotext-fallback":
        draft_heading = "## 文字層初稿（Docling 後備）"
        export_note = (
            "候選頁以整頁 `pdftoppm` 匯出，並以 vision／VLM 補 Visual Evidence"
        )
    else:
        draft_heading = "## 文字層初稿（pdftotext／fast）"
        export_note = (
            "候選頁以整頁 `pdftoppm` 匯出，並以 vision／VLM 補 Visual Evidence"
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
            f"{export_note}"
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
            "engine": args.engine,
            "page_from": page_from,
            "page_to": page_to,
            "char_threshold": args.char_threshold,
            "image_area": args.image_area,
            "vision_pages": vision_pages,
            "triage": [asdict(item) for item in triage],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

        need_draft = not args.triage_only
        need_export = args.export_vision_assets
        use_docling = args.engine == ENGINE_DOCLING
        force_page_render = args.force_page_render or not use_docling
        extract_images = need_export and use_docling and not force_page_render
        docling_document = None
        engine = args.engine if use_docling else ENGINE_FAST
        markdown = ""

        if use_docling and (need_draft or extract_images):
            try:
                converted = convert_with_docling(
                    pdf,
                    page_from,
                    page_to,
                    extract_images=extract_images,
                    images_scale=images_scale_for_dpi(args.dpi),
                )
                markdown = converted.markdown
                docling_document = converted.document
                engine = ENGINE_DOCLING
            except RuntimeError as error:
                if need_draft and args.no_fallback:
                    raise
                if need_draft:
                    print(
                        "docling-pdf: Docling unavailable, "
                        f"fallback to pdftotext ({error})",
                        file=sys.stderr,
                    )
                    markdown = convert_with_pdftotext_fallback(
                        pdf, page_from, page_to
                    )
                    engine = "pdftotext-fallback"
                else:
                    print(
                        "docling-pdf: picture extract unavailable, "
                        f"using pdftoppm ({error})",
                        file=sys.stderr,
                    )
        elif need_draft:
            markdown = convert_with_pdftotext_fallback(pdf, page_from, page_to)
            engine = ENGINE_FAST

        if need_export:
            written = export_vision_assets(
                pdf,
                base_slug,
                vision_pages,
                total_pages,
                args.dpi,
                min_image_area=args.image_area,
                document=docling_document,
                force_page_render=force_page_render,
                page_from=page_from,
                page_to=page_to,
            )
            print(
                json.dumps(
                    {
                        "exported_assets": [
                            {
                                "path": str(item.path.relative_to(ROOT)),
                                "page": item.page,
                                "method": item.method,
                                "width": item.width,
                                "height": item.height,
                            }
                            for item in written
                        ]
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

        if args.triage_only:
            return 0

        out = (
            resolve_path(args.out)
            if args.out
            else temp_path(f"{base_slug}-pdf-draft.md")
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
