---
name: llm-wiki-lint
description: LLM Wiki Lint。使用者輸入 /lint、lint、檢查 wiki、品質檢查時使用。步驟見 docs/PROMPTS.md 的 Lint 提示詞；規約見 AGENTS.md。
---

# /lint

## 觸發

`/lint`、`lint`、檢查 wiki、品質檢查、wiki lint

## 執行

1. 遵循 [AGENTS.md](../../../AGENTS.md)（含 **操作：Lint**、硬約束）。
2. **依全文執行** [docs/PROMPTS.md](../../../docs/PROMPTS.md) 的 **## Lint 提示詞** — 勿在本 Skill 改寫或省略步驟。
3. 產物寫入 `wiki/lint/`；必要時於 `wiki/index.md` **Overview** 掛連結；**一律** append `wiki/log.md`。
