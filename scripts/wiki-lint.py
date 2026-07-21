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
                (p for p in sources if fm(p.read_text(encoding="utf-8")).get("resource") == slug),
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


def main() -> int:
    err: list[str] = []
    check_type(err)
    check_links(err)
    check_resource(err)
    check_visual(err)
    if err:
        print(f"wiki-lint: {len(err)} issue(s)", file=sys.stderr)
        print("\n".join(err), file=sys.stderr)
        return 1
    print("wiki-lint: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
