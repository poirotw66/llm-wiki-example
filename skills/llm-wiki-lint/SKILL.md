---
name: llm-wiki-lint
description: LLM Wiki Lint。使用者輸入 /lint、lint、檢查 wiki、品質檢查時使用。步驟見 docs/PROMPTS.md 的 Lint 提示詞；規約見 AGENTS.md。
---

# /lint

## 觸發

`/lint`、`lint`、檢查 wiki、品質檢查、wiki lint

## 執行

1. **先執行** `uv run --group test python3 scripts/wiki-lint.py`（exit 0 後再繼續）。
2. 遵循工作區根目錄 **AGENTS.md**（含 **操作：Lint**、硬約束）。
3. **依全文執行** 工作區根目錄 **docs/PROMPTS.md** 的 **## Lint 提示詞** — 勿在本 Skill 改寫或省略步驟。
4. 操作一開始以本次 log title 執行 `python3 scripts/wiki-usage.py start lint --title "<title>"`；產物寫入 `wiki/lint/`；必要時於 `wiki/index.md` **Overview** 掛連結；**一律** append `wiki/log.md`，再執行 `python3 scripts/wiki-usage.py finish lint --title "<title>"`。
