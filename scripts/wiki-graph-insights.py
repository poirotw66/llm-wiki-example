#!/usr/bin/env python3
"""Emit structural wiki graph insights as Markdown (no UI).

Writes ``wiki/graph/insights.md`` by default (reserved filename; not an OKF Concept).
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
RAW_SOURCES = ROOT / "raw" / "sources"
SKIP = frozenset(
    {"index.md", "log.md", "README.md", "purpose.md", "queue.md", "insights.md"}
)
LINKS = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+\.md(?:#[^)]+)?)\)")
ROLE_DIRS = ("sources", "concepts", "entities", "queries", "faq", "lint", "graph")


def wiki_pages() -> list[Path]:
    return sorted(path for path in WIKI.rglob("*.md") if path.name not in SKIP)


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def role_of(path: Path) -> str:
    try:
        return path.relative_to(WIKI).parts[0]
    except ValueError:
        return ""


def build_graph(
    pages: list[Path],
) -> tuple[dict[Path, set[Path]], dict[Path, int]]:
    page_set = set(pages)
    outbound: dict[Path, set[Path]] = defaultdict(set)
    inbound: dict[Path, int] = defaultdict(int)
    for path in pages:
        text = path.read_text(encoding="utf-8")
        for target in LINKS.findall(text):
            rel = target.split("#", 1)[0].strip()
            if not rel or rel.startswith(("http://", "https://", "/")):
                continue
            destination = (path.parent / rel).resolve()
            if destination in page_set and destination != path:
                outbound[path].add(destination)
                inbound[destination] += 1
    return outbound, inbound


def wiki_link(path: Path) -> str:
    return f"[{relative(path)}](../{path.relative_to(WIKI).as_posix()})"


def render(
    pages: list[Path],
    outbound: dict[Path, set[Path]],
    inbound: dict[Path, int],
) -> str:
    today = dt.date.today().isoformat()
    isolated: list[Path] = []
    orphans: list[Path] = []
    bridges: list[tuple[Path, set[str]]] = []
    one_way: list[tuple[Path, Path]] = []

    for path in pages:
        degree = inbound[path] + len(outbound[path])
        if degree <= 1:
            isolated.append(path)
        if inbound[path] == 0:
            orphans.append(path)
        roles = {
            role_of(target)
            for target in outbound[path]
            if role_of(target) in ROLE_DIRS
        }
        if len(roles) >= 2:
            bridges.append((path, roles))
        for target in outbound[path]:
            if path not in outbound.get(target, set()):
                one_way.append((path, target))

    missing_sources: list[str] = []
    if RAW_SOURCES.is_dir():
        wiki_source_stems = {
            path.stem for path in pages if path.parent == WIKI / "sources"
        }
        for archive in sorted(RAW_SOURCES.glob("*.md")):
            if archive.stem not in wiki_source_stems:
                missing_sources.append(archive.name)

    lines = [
        "# Graph insights",
        "",
        f"Generated: {today}",
        "",
        "> Structural report from `scripts/wiki-graph-insights.py`. Not an OKF Concept.",
        "",
        "## Summary",
        "",
        f"- pages scanned: {len(pages)}",
        f"- isolated (degree ≤ 1): {len(isolated)}",
        f"- no inbound link: {len(orphans)}",
        f"- bridge pages (≥2 role dirs): {len(bridges)}",
        f"- one-way links: {len(one_way)}",
        f"- raw archives missing wiki/sources page: {len(missing_sources)}",
        "",
        "## Isolated pages",
        "",
    ]
    if isolated:
        lines.extend(f"- {wiki_link(path)}" for path in isolated)
    else:
        lines.append("- （無）")

    lines.extend(["", "## No inbound link", ""])
    if orphans:
        lines.extend(f"- {wiki_link(path)}" for path in orphans)
    else:
        lines.append("- （無）")

    lines.extend(["", "## Bridge pages", ""])
    if bridges:
        for path, roles in bridges:
            role_text = ", ".join(sorted(roles))
            lines.append(f"- {wiki_link(path)} — roles: {role_text}")
    else:
        lines.append("- （無）")

    lines.extend(["", "## One-way links (A→B without B→A)", ""])
    if one_way:
        for source, target in one_way[:50]:
            lines.append(f"- {relative(source)} → {relative(target)}")
        if len(one_way) > 50:
            lines.append(f"- … and {len(one_way) - 50} more")
    else:
        lines.append("- （無）")

    lines.extend(["", "## Raw archives without wiki/sources page", ""])
    if missing_sources:
        lines.extend(f"- `raw/sources/{name}`" for name in missing_sources)
    else:
        lines.append("- （無）")

    lines.extend(
        [
            "",
            "## Agent follow-up",
            "",
            "- Review isolated / no-inbound pages for missing cross-links.",
            "- Scan bridge pages for **contradictions** (Agent judgment; not auto-detected).",
            "- Create missing wiki/sources pages for raw archives (ingest guarantee).",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=str(WIKI / "graph" / "insights.md"),
        help="Output Markdown path (default: wiki/graph/insights.md)",
    )
    args = parser.parse_args(argv)
    pages = wiki_pages()
    if not pages:
        print("wiki-graph-insights: no concept pages; skipped")
        return 0
    outbound, inbound = build_graph(pages)
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(pages, outbound, inbound), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
