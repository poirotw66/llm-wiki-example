#!/usr/bin/env python3
"""Minimal OKF wiki bundle linter (stdlib only)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI, RAW_SOURCES, RAW_ASSETS = ROOT / "wiki", ROOT / "raw/sources", ROOT / "raw/assets"
SKIP = frozenset({"index.md", "log.md", "README.md"})
FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
LINKS = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
VE_HEAD = re.compile(
    r"(?:^|\n)(?:#{2,4}\s*)?(?:\*\*)?Visual Evidence(?:\*\*)?[^\n]*\n",
    re.IGNORECASE,
)
VE_BAN = (
    "細節以原圖為準",
    "請見原圖",
    "請看原圖",
    "略過圖內",
    "圖略",
)
VE_NODE = re.compile(r"層\s*[／/]\s*節點|節點盤點|架構層級")
VE_FLOW = re.compile(r"資料流|控制流|主要資料流|→")
ASSET_EMBED = re.compile(
    r"!\[[^\]]*\]\((?:(?:\.\./)+)assets/[^)\s]+/p\d+\.png\)"
)
H2_VE = re.compile(r"(?m)^## Visual Evidence\s*$")
H2_ANY = re.compile(r"(?m)^## ")


def fm(text: str) -> dict[str, str]:
    m = FM.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip("\"'")
    return out


def wiki_pages() -> list[Path]:
    return [p for p in WIKI.rglob("*.md") if p.name not in SKIP]


def split_visual_evidence_blocks(text: str) -> list[str]:
    starts = [m.start() for m in VE_HEAD.finditer(text)]
    if not starts:
        return []
    starts.append(len(text))
    return [text[starts[i] : starts[i + 1]].strip() for i in range(len(starts) - 1)]


def visual_evidence_issues(block: str) -> list[str]:
    issues: list[str] = []
    for phrase in VE_BAN:
        if phrase in block:
            issues.append(f"banned phrase {phrase!r}")
    if not VE_NODE.search(block):
        issues.append("missing 層／節點盤點")
    if not VE_FLOW.search(block):
        issues.append("missing 資料流／控制流")
    body = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", block)
    body = re.sub(r"(?m)^[-*]\s*\*\*[^*]+\*\*[：:].*$", "", body)
    compact = re.sub(r"\s+", "", body)
    if len(compact) < 120:
        issues.append("structured transcription too short")
    return issues


def visual_evidence_placement_issues(text: str) -> list[str]:
    """Reject end-of-file dumps of all asset embeds under ## Visual Evidence."""
    issues: list[str] = []
    all_embeds = ASSET_EMBED.findall(text)
    if len(all_embeds) < 2:
        return issues
    for match in H2_VE.finditer(text):
        start = match.end()
        next_h2 = H2_ANY.search(text, start)
        section = text[start : next_h2.start()] if next_h2 else text[start:]
        section_embeds = ASSET_EMBED.findall(section)
        if len(section_embeds) >= 2 and len(section_embeds) == len(all_embeds):
            issues.append(
                "Visual Evidence dumped at end under ## Visual Evidence; "
                "place each block inline under its page/section"
            )
            break
    return issues


def check_links(err: list[str]) -> None:
    for path in wiki_pages():
        text = path.read_text(encoding="utf-8")
        for target in LINKS.findall(text) + IMG.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            rel = target.split("#", 1)[0]
            if not rel:
                continue
            if rel.startswith("/"):
                err.append(f"root-path link: {path.relative_to(ROOT)} -> {target}")
                continue
            if not (path.parent / rel).resolve().is_file():
                err.append(f"broken link: {path.relative_to(ROOT)} -> {target}")


def check_type(err: list[str]) -> None:
    for path in wiki_pages():
        if not fm(path.read_text(encoding="utf-8")).get("type"):
            err.append(f"missing frontmatter type: {path.relative_to(ROOT)}")


def check_resource(err: list[str]) -> None:
    for path in wiki_pages():
        res = fm(path.read_text(encoding="utf-8")).get("resource", "")
        if not res or res.startswith("http"):
            continue
        slug = res.removesuffix(".md").split("/")[-1]
        if not (RAW_SOURCES / f"{slug}.md").is_file():
            err.append(f"missing raw archive: {path.relative_to(ROOT)} resource={res}")


def check_visual(err: list[str]) -> None:
    if not RAW_ASSETS.is_dir():
        return
    sources = list((WIKI / "sources").glob("*.md"))
    for d in sorted(p for p in RAW_ASSETS.iterdir() if p.is_dir()):
        if not list(d.glob("p*.png")):
            continue
        slug = d.name
        page = WIKI / "sources" / f"{slug}.md"
        if not page.is_file():
            page = next(
                (
                    p
                    for p in sources
                    if fm(p.read_text(encoding="utf-8")).get("resource") == slug
                ),
                None,
            )
        if page is None:
            err.append(f"visual assets without wiki source: raw/assets/{slug}/")
            continue
        text = page.read_text(encoding="utf-8")
        if "## Visual Assets" not in text:
            err.append(f"missing ## Visual Assets: {page.relative_to(ROOT)}")
            continue
        embeds = [t for t in IMG.findall(text) if f"raw/assets/{slug}/" in t]
        if not embeds:
            err.append(f"no visual embeds: {page.relative_to(ROOT)} (raw/assets/{slug}/)")
        for target in embeds:
            rel = target.split("#", 1)[0]
            if not (page.parent / rel).resolve().is_file():
                err.append(f"broken visual embed: {page.relative_to(ROOT)} -> {target}")


def check_visual_evidence(err: list[str]) -> None:
    """Fail hollow Visual Evidence in archives referenced by wiki sources."""
    sources_dir = WIKI / "sources"
    if not sources_dir.is_dir():
        return
    for page in sorted(sources_dir.glob("*.md")):
        page_text = page.read_text(encoding="utf-8")
        meta = fm(page_text)
        res = meta.get("resource", "")
        if not res or res.startswith("http"):
            continue
        slug = res.removesuffix(".md").split("/")[-1]
        archive = RAW_SOURCES / f"{slug}.md"
        if not archive.is_file():
            continue
        text = archive.read_text(encoding="utf-8")
        blocks = split_visual_evidence_blocks(text)
        if "## Visual Assets" in page_text and not blocks:
            am = fm(text)
            asset_slug = am.get("base-slug") or slug
            asset_dir = RAW_ASSETS / asset_slug
            if asset_dir.is_dir() and list(asset_dir.glob("p*.png")):
                err.append(
                    "wiki has visuals but archive lacks Visual Evidence: "
                    f"{archive.relative_to(ROOT)}"
                )
            continue
        for index, block in enumerate(blocks, start=1):
            for issue in visual_evidence_issues(block):
                err.append(
                    f"weak Visual Evidence #{index} in "
                    f"{archive.relative_to(ROOT)}: {issue}"
                )
        for issue in visual_evidence_placement_issues(text):
            err.append(f"{issue}: {archive.relative_to(ROOT)}")


def main() -> int:
    err: list[str] = []
    check_type(err)
    check_links(err)
    check_resource(err)
    check_visual(err)
    check_visual_evidence(err)
    if err:
        print(f"wiki-lint: {len(err)} issue(s)", file=sys.stderr)
        print("\n".join(err), file=sys.stderr)
        return 1
    print("wiki-lint: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
