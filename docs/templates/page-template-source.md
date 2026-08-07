---
title: "<來源頁標題>"
type: source
description: "<一語摘要（OKF 建議）>"
resource: "<來源的 canonical URI；無 URI 時可省略>"
archive_slug: "<對應 raw/sources/<slug>.md 的 slug>"
analysis_receipt:
  version: "1"
  sha256: "<兩段式分析稿 SHA-256；不寫入分析正文>"
  source_sha256: "<raw/sources canonical 檔 SHA-256>"
  generated_by: "<agent/version|human:id|process:id>"
  generated_at: "YYYY-MM-DDTHH:MM:SSZ"
tags: []
sources:
  - id: archive
    resource: "../../raw/sources/<slug>.md"
    title: "<歸檔稿標題>"
generated: { by: "<agent/version|human:id|process:id>", at: "YYYY-MM-DDTHH:MM:SSZ" }
status: draft
stale_after: "YYYY-MM-DD"
classification: internal
owner: "team:<id>"
access_scope: "team:<id>"
contains_pii: unknown
retention: "per-policy:<id>"
redaction: required
---

# <來源頁標題>

> 本版型 **僅** 供 `wiki/sources/*` 使用。區塊標題須與 **AGENTS.md** → **來源頁 Schema** 一致。Frontmatter 對齊 [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) + 本倉治理擴充（見 [docs/okf.md](../okf.md)、[data-governance.md](../data-governance.md)）。

## Summary

- 要點 1
- 要點 2
- 要點 3

## Key Concepts

- 概念或術語 — 簡短說明；可連結例如 [概念](../concepts/....md)

## Entities

- 系統或產品 — 簡短說明；可連結例如 [實體](../entities/....md)

## Notable Claims

- 可驗證主張，附引用 [本來源頁](./<slug>.md) 或 `../../raw/sources/<slug>.md`。[^archive]

## Visual Assets

> 來源含架構圖、流程圖等資訊性視覺時 **必填**；無視覺資產時可省略整節。路徑自 `wiki/sources/` 指向 `raw/assets/`（見 **docs/visual-source-conversion.md**）。

- [圖說（PDF 第 N 頁）](../../raw/assets/<base-slug>/p<NN>.png)

![圖說](../../raw/assets/<base-slug>/p<NN>.png)

## Limitations / Gaps

- 來源未涵蓋之處、模糊之處或後續待辦。

## Relationships

- related_to: [概念](../concepts/....md)
- used_in: [實體](../entities/....md)

[^archive]: `<歸檔稿標題>`
