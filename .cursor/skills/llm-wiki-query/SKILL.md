---
name: llm-wiki-query
description: LLM Wiki Query。使用者輸入 /query、query、向 wiki 提問、查知識庫時使用。步驟見 docs/PROMPTS.md 的 Query 提示詞；規約見 AGENTS.md。
---

# /query

## 觸發

`/query`、`query`、提問、查 wiki、知識庫問答

## 執行

1. 遵循 [AGENTS.md](../../../AGENTS.md)（含 **操作：Query**、**Query 解析規則**、硬約束）。
2. **依全文執行** [docs/PROMPTS.md](../../../docs/PROMPTS.md) 的 **## Query 提示詞** — 勿在本 Skill 改寫或省略步驟。
3. 可重用答案時寫入 `wiki/queries/` 並更新 index；**一律** append `wiki/log.md`（僅回答時記 pass／no-op）。

## 使用者輸入

訊息中的問題為本次查詢；答案須附引用與不確定性標記。
