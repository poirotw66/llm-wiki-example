---
name: llm-wiki-query
description: LLM Wiki Query。使用者輸入 /query、query、向 wiki 提問、查知識庫時使用。步驟見 docs/PROMPTS.md 的 Query 提示詞；規約見 AGENTS.md。
---

# /query

## 觸發

`/query`、`query`、提問、查 wiki、知識庫問答

## 執行

1. 遵循工作區根目錄 **AGENTS.md**（含 **操作：Query**、**Query 解析規則**、硬約束）。
2. **依全文執行** 工作區根目錄 **docs/PROMPTS.md** 的 **## Query 提示詞** — 勿在本 Skill 改寫或省略步驟。
3. 操作一開始以本次 log title 執行 `python3 scripts/wiki-usage.py start query --title "<title>"`；可重用答案時寫入 `wiki/queries/` 並更新 index；**一律** append 相同 title 的 `wiki/log.md`（僅回答時記 pass／no-op），再執行 `python3 scripts/wiki-usage.py finish query --title "<title>"`。若漏掉 start，finish 會自動復原量測且拒絕 0 token。

## 視覺答案

若問題涉及架構圖等資訊性視覺，答案 **必須** embed `raw/assets/` 原圖（見 **docs/visual-source-conversion.md** → **可檢索原圖**、**PROMPTS.md** § Query 步驟 6）。若須重新讀圖分析，依 **平行 Vision 編排** **派 subagent**；主 Agent 禁止自行 `Read` 圖片。

## 使用者輸入

訊息中的問題為本次查詢；答案須附引用與不確定性標記。
