---
name: llm-wiki-faq
description: LLM Wiki FAQ。使用者輸入 /faq、faq、產生 FAQ、題組頁時使用。步驟見 docs/PROMPTS.md 的 FAQ 提示詞；規約見 AGENTS.md。
---

# /faq

## 觸發

`/faq`、`faq`、產生 FAQ、建立題組、常見問題整理

## 執行

1. 遵循工作區根目錄 **AGENTS.md**（含 **操作：FAQ**、**FAQ 頁格式**、**FAQ 規則**）。
2. **依全文執行** 工作區根目錄 **docs/PROMPTS.md** 的 **## FAQ 提示詞** — 勿在本 Skill 改寫或省略步驟。
3. 操作一開始以本次 log title 執行 `python3 scripts/wiki-usage.py start faq --title "<title>"`；產物寫入 `wiki/faq/`；更新 `wiki/index.md` FAQ 區；append `wiki/log.md`，再執行 `python3 scripts/wiki-usage.py finish faq --title "<title>"`。
