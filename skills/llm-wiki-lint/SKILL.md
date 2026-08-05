---
name: llm-wiki-lint
description: LLM Wiki Lint。使用者輸入 /lint、lint、檢查 wiki、品質檢查時使用。步驟見 docs/PROMPTS.md 的 Lint 提示詞；規約見 AGENTS.md。
---

# /lint

## 觸發

`/lint`、`lint`、檢查 wiki、品質檢查、wiki lint

## 執行

1. 遵循工作區根目錄 **AGENTS.md**（含 **操作：Lint**、硬約束）。
2. **依全文執行**工作區根目錄 **docs/PROMPTS.md** 的 **## Lint 提示詞**；該章負責 telemetry、auto lint、深度檢查與留痕順序。
3. 使用 **docs/PROMPTS.md** 定義的共用 telemetry wrapper；勿在本 Skill 複製或改寫操作步驟。
