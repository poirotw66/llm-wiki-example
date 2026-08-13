#!/usr/bin/env python3
"""Reset wiki knowledge + raw archives back to a blank template state.

Keeps: wiki/lint/*, ops/purpose.md, docs/, scripts/, and log history
(append-only). Rewrites wiki/index.md to the blank catalog. Requires
``--confirm``; default is dry-run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

_SCRIPTS = str(Path(__file__).resolve().parent)
if _SCRIPTS not in sys.path:  # scripts/ uses hyphenated, unimportable filenames.
    sys.path.append(_SCRIPTS)

from _common import ROOT, Paths

#: Bundle being reset.  ``configure`` repoints every location at once.
PATHS = Paths(ROOT)

#: Emptied on reset.  Stored as names so the sets cannot fall out of step with
#: the configured root; ``wiki/lint/`` is deliberately absent, it is preserved.
KNOWLEDGE_DIR_NAMES = ("sources", "concepts", "entities", "queries", "faq", "graph")
RAW_CONTENT_DIR_NAMES = ("inbox", "originals", "sources", "assets")
PRESERVE_NAMES = {".gitkeep"}

BLANK_INDEX = """\
---
okf_version: "0.2"
---

# Index

## Overview

- 本 repo **llm-wiki-example** 為各部門可 fork 的 **OKF v0.2 Knowledge Bundle 範本**（見 [docs/okf.md](../docs/okf.md)）。
- **方向**：[Purpose](../ops/purpose.md) — 目標、關鍵問題、範圍（與 AGENTS／PROMPTS 操作 schema 分離）。
- **人審佇列**：[Review Queue](../ops/review-queue.md) — Ingest 非同步標出需人工項目。
- 寫入或分享內容前，須依 [企業資料治理](../docs/data-governance.md) 完成分類、PII、遮罩、owner 與 Git 准入確認。
- [企業治理與 OKF v0.2 生產化強化](./lint/企業治理與OKF-v0.2強化.md) — 本輪治理、cleanup、schema lint、CI 與遷移驗證摘要。
- 採用見 [README](../README.md)、[docs/onboarding.md](../docs/onboarding.md)、[SKILL.md](../SKILL.md)。
- 規約：[AGENTS.md](../AGENTS.md)；提示詞：[docs/PROMPTS.md](../docs/PROMPTS.md)；`wiki/` 導覽：[Bundle 導覽](../docs/wiki-bundle.md)。
- `wiki/` **刻意留白** — 請以第一份來源執行 `/ingest` 後更新本目錄。

## Concepts

（尚無內容 — 請 Ingest 後更新）

## Entities

（尚無內容 — 請 Ingest 後更新）

## Sources

（尚無內容 — 請 Ingest 後更新）

## Queries

（尚無內容 — 請 Query 持久化後更新）

## FAQ

（尚無內容 — 請 FAQ 操作後更新）
"""

BLANK_REVIEW = """\
# Review Queue

Async human-in-the-loop items. Ingest／Lint may append here without blocking wiki writes.
Close items with `python3 scripts/ingest-review.py close --id <id>`.

## Open

## Done
"""


def configure(root: Path | str) -> Paths:
    """Point every location at ``root``; returns the resulting layout."""
    global PATHS
    PATHS = Paths(Path(root))
    return PATHS


def knowledge_dirs() -> tuple[Path, ...]:
    return tuple(PATHS.wiki / name for name in KNOWLEDGE_DIR_NAMES)


def raw_content_dirs() -> tuple[Path, ...]:
    return tuple(PATHS.raw / name for name in RAW_CONTENT_DIR_NAMES)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Reset wiki knowledge pages and raw archives to a blank template. "
            "Keeps wiki/lint/. Default is dry-run; pass --confirm to apply."
        )
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually delete knowledge/raw content and rewrite index",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without changing files (default)",
    )
    parser.add_argument(
        "--skip-log",
        action="store_true",
        help="Do not append wiki/log.md (still prints the planned entry)",
    )
    parser.add_argument("--root", help="Bundle root to reset (default: this repository)")
    return parser


def list_removals() -> list[Path]:
    """Return files and directories that would be removed."""
    targets: list[Path] = []
    for directory in knowledge_dirs():
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.name not in PRESERVE_NAMES:
                targets.append(path)
    for directory in raw_content_dirs():
        if not directory.is_dir():
            continue
        for path in sorted(directory.iterdir()):
            if path.name in PRESERVE_NAMES:
                continue
            targets.append(path)
    return targets


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def ensure_gitkeeps() -> None:
    for directory in (*knowledge_dirs(), *raw_content_dirs()):
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")


def append_log(log_path: Path, title: str, detail_lines: list[str]) -> None:
    today = dt.date.today().isoformat()
    heading = f"## {today}"
    block_lines = [f"- **lint** | {title}", *[f"  - {line}" for line in detail_lines]]
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Wiki Log\n"
    if heading in existing:
        updated = existing.rstrip() + "\n\n" + "\n".join(block_lines) + "\n"
    else:
        updated = existing.rstrip() + f"\n\n{heading}\n\n" + "\n".join(block_lines) + "\n"
    log_path.write_text(updated, encoding="utf-8")


def reset_wiki(*, confirmed: bool, skip_log: bool) -> int:
    targets = list_removals()
    index_path = PATHS.index
    log_path = PATHS.log
    review_path = PATHS.review_queue
    cache_path = PATHS.ingest_cache
    analyses_dir = PATHS.ingest_analyses
    print(f"planned removals: {len(targets)}")
    for path in targets:
        print(f"  - {PATHS.relative(path)}")
    print(f"  - rewrite {PATHS.relative(index_path)} (blank catalog)")
    print(f"  - rewrite {PATHS.relative(review_path)} (empty queue)")
    print("  - clear ingest cache/analyses under .llm-wiki/ingest/")
    if not skip_log:
        print(f"  - append {PATHS.relative(log_path)}")

    if not confirmed:
        print("dry-run: would reset (--confirm is required)")
        return 0

    for path in targets:
        remove_path(path)
    ensure_gitkeeps()
    index_path.write_text(BLANK_INDEX, encoding="utf-8")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(BLANK_REVIEW, encoding="utf-8")
    if cache_path.is_file():
        cache_path.unlink()
    if analyses_dir.is_dir():
        shutil.rmtree(analyses_dir)
    if not skip_log:
        append_log(
            log_path,
            "初始化 wiki 回範本空白",
            [
                "執行 `scripts/wiki-reset.py --confirm`：清除 knowledge 頁與 raw 歸檔／inbox 內容。",
                "還原 `wiki/index.md` 為刻意留白；清空 review queue 與 ingest cache；保留 `wiki/lint/`、`ops/purpose.md`。",
            ],
        )
    print("reset complete")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.root:
        configure(args.root)
    confirmed = bool(args.confirm) and not bool(args.dry_run)
    try:
        return reset_wiki(confirmed=confirmed, skip_log=args.skip_log)
    except OSError as error:
        print(f"wiki-reset: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
