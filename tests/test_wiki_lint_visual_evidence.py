"""Tests for Visual Evidence quality lint rules."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_lint():
    path = Path(__file__).resolve().parents[1] / "scripts" / "wiki-lint.py"
    spec = importlib.util.spec_from_file_location("wiki_lint", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules["wiki_lint"] = module
    spec.loader.exec_module(module)
    return module


def test_hollow_visual_evidence_is_rejected() -> None:
    module = _load_lint()
    block = """
#### Visual Evidence — 第 5 頁

- **資產**：../assets/x/p05.png
- **結構化轉寫**：
  - 細節以原圖為準。
"""
    issues = module.visual_evidence_issues(block)
    assert any("banned phrase" in item for item in issues)
    assert any("節點" in item for item in issues)


def test_complete_visual_evidence_passes() -> None:
    module = _load_lint()
    block = """
#### Visual Evidence — 第 5 頁

![圖](../assets/x/p05.png)

- **資產**：../assets/x/p05.png
- **來源位置**：PDF 第 5 頁
- **層／節點盤點**：
  | 層級 | 元件 |
  |------|------|
  | 程式 | ACP0_B050 地址擷取 |
  | 檔案 | DTACP020 當批應催繳檔；DTACP205 地址檔 |
- **主要資料流**：
  1. DTACP020 → ACP0_B050 → DTACP205 → ACP0_B051 → DTACP207
  2. DTACP207 → ACP0_B052 → DTACP022
"""
    assert module.visual_evidence_issues(block) == []


def test_end_dumped_visual_evidence_is_rejected() -> None:
    module = _load_lint()
    text = """
# Doc

## 1 Intro

Text only.

## Visual Evidence

### [圖1]

![a](../assets/demo/p02.png)

#### Visual Evidence — p02

- **層／節點盤點**：A, B
- **主要資料流**：A → B → C with enough filler text for length checks if needed elsewhere

### [圖2]

![b](../assets/demo/p04.png)

#### Visual Evidence — p04

- **層／節點盤點**：X, Y
- **主要資料流**：X → Y

## Limitations / Gaps

- none
"""
    issues = module.visual_evidence_placement_issues(text)
    assert any("dumped at end" in item for item in issues)


def test_inline_visual_evidence_placement_passes() -> None:
    module = _load_lint()
    text = """
# Doc

## 1.2 Flow

#### Visual Evidence — 第 2 頁

![a](../assets/demo/p02.png)

- **層／節點盤點**：A
- **主要資料流**：A → B

## 1.4 Batch

#### Visual Evidence — 第 4 頁

![b](../assets/demo/p04.png)

- **層／節點盤點**：X
- **主要資料流**：X → Y

## Limitations / Gaps

- none
"""
    assert module.visual_evidence_placement_issues(text) == []
