---
name: llm-wiki-ingest
description: LLM Wiki Ingest。使用者輸入 /ingest、ingest、歸檔、收斂來源、納入 wiki 時使用。步驟單一來源為 docs/PROMPTS.md 的 Ingest 提示詞；規約見 AGENTS.md。
---

# /ingest

## 觸發

`/ingest`、`ingest`、歸檔、Ingest、收斂來源、納入 wiki

## 執行

1. 遵循工作區根目錄 **AGENTS.md**（含 **操作：Ingest**、硬約束、`raw/` 不可變）。
2. **依全文執行** 工作區根目錄 **docs/PROMPTS.md** 的 **## Ingest 提示詞** — 勿在本 Skill 改寫或省略步驟。
3. 完成後確認 `wiki/index.md` 已更新（若適用）、`wiki/log.md` 已 append。

## 使用者輸入

訊息中的檔案路徑、URL 或貼上內容為本次 **指定來源**。未提供時請向使用者索取。
