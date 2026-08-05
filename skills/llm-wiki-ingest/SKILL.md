---
name: llm-wiki-ingest
description: LLM Wiki Ingest。使用者輸入 /ingest、ingest、歸檔、收斂來源、納入 wiki 時使用。含多模態 triage／轉檔（見 docs/ingest-pipeline.md；PDF 見 docs/pdf-ingest-sop.md；視覺硬閘見 docs/visual-source-conversion.md）；步驟見 docs/PROMPTS.md；規約見 AGENTS.md。
---

# /ingest

## 觸發

`/ingest`、`ingest`、歸檔、Ingest、收斂來源、納入 wiki

## 執行

1. 遵循工作區根目錄 **AGENTS.md**（含 **操作：Ingest**、硬約束與資料治理）。
2. **依全文執行**工作區根目錄 **docs/PROMPTS.md** 的 **## Ingest 提示詞**；技術細節依該章引用的 Ingest／PDF／視覺 SOP。
3. 使用 **docs/PROMPTS.md** 定義的共用 telemetry wrapper；勿在本 Skill 複製或改寫操作步驟。

## 使用者輸入

訊息中的檔案路徑、URL 或貼上內容為本次 **指定來源**。未提供時請向使用者索取。
