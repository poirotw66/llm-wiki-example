---
title: "<Page title>"
type: concept
description: "<一語摘要（OKF 建議）>"
resource: "<canonical URI；抽象 concept 可省略>"
tags: []
sources:
  - id: source-1
    resource: "../sources/<source-page>.md"
    title: "<來源標題>"
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

# <Page title>

> 本版型供 `wiki/concepts/*`、`wiki/entities/*`、`wiki/queries/*` 起稿。`type` 改為 `concept` | `entity` | `query`。所有 placeholder 均須在提交前依 [data-governance.md](../data-governance.md) 人工確認；區塊為 **建議**（見 **AGENTS.md** → Concept／Entity／Query／Lint 頁）。

## Summary

一段概述。

## Key Points

- 要點並引用 [來源](../sources/....md)。[^source-1]

## Evidence

- 有根據的主張 → [來源](../sources/....md) 或 `../../raw/sources/<slug>.md`

## Relationships

- related_to: [概念](../concepts/....md)
- implemented_by: [實體](../entities/....md)

## Open Questions

- 待釐清事項（選填）

[^source-1]: <來源標題>
