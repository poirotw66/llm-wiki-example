---
type: lint
title: "企業治理與 OKF v0.2 生產化強化"
description: "記錄資料治理、cleanup 防呆、YAML/schema lint、CI 與 OKF v0.2 遷移的完成狀態。"
tags: [governance, okf-v0.2, lint, ci]
sources:
  - id: governance
    resource: "../../docs/data-governance.md"
    title: "企業資料治理"
  - id: okf-mapping
    resource: "../../docs/okf.md"
    title: "OKF v0.2 對照、治理與互通"
  - id: repository-rules
    resource: "../../AGENTS.md"
    title: "LLM Wiki 規約"
generated: { by: "codex/gpt-5.6-sol", at: "2026-08-05T12:00:00+08:00" }
verified: { by: "process:wiki-quality-ci", at: "2026-08-05T12:00:00+08:00" }
status: stable
stale_after: "2027-02-05"
classification: internal
owner: "process:repository-maintenance"
access_scope: organization
contains_pii: false
retention: permanent
redaction: none
---

# 企業治理與 OKF v0.2 生產化強化

## Summary

- 本示範專案已全面採用 OKF v0.2；模板、規約、parser 與既有示範內容不保留舊格式相容分支。[^okf-mapping]
- 已建立資料分類、owner、access scope、PII、retention、redaction 與 Git 准入規則。[^governance]
- cleanup 現在預設 dry-run，僅在 originals 位元一致、canonical source 存在且明確 `--confirm` 時刪除 allowlist 內的輸入副本。[^repository-rules]
- wiki lint 改用真正 YAML parser，並檢查 v0.2 schema、治理欄位、索引、連結、生命週期與 Git history invariants。
- GitHub Actions 會以 Python 3.12／uv 執行完整測試及帶 Git base 的 wiki lint。

## Verification

- `uv run --group test python3 -m pytest -q`
- `uv run --group test python3 scripts/wiki-lint.py`
- `git diff --check`

## Limitations / Gaps

- lint 會拒絕非 v0.2 metadata、lifecycle、bare resource slug、非 keyed provenance 與非日期分組 log。
- `classification` 與 `access_scope` 是 metadata，不取代 repository、object storage 或 retrieval runtime 的實際 ACL。[^governance]
- CI 驗證 Git 中的結構與歷史；秘密掃描、法遵審批及外部儲存權限仍須由企業平台另行提供。

## Relationships

- governed_by: [LLM Wiki 規約](../../AGENTS.md)
- related_to: [OKF v0.2 對照](../../docs/okf.md)
- cataloged_in: [Index](../index.md)

[^governance]: 企業資料治理與 Git 准入規則。
[^okf-mapping]: OKF v0.2 遷移與相容決策。
[^repository-rules]: Repository Ingest、Lint 與硬約束。
