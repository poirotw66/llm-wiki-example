---
name: llm-wiki-graph
description: LLM Wiki Graph。使用者輸入 /graph、graph、知識圖、關係圖、knowledge map 時使用。步驟見 docs/PROMPTS.md 的 Graph 提示詞；規約見 AGENTS.md。
---

# /graph

## 觸發

`/graph`、`graph`、知識圖、關係圖、knowledge map、建立 graph

## 執行

1. 遵循工作區根目錄 **AGENTS.md**（含 **操作：Graph**、連結與關係規則）。
2. **依全文執行** 工作區根目錄 **docs/PROMPTS.md** 的 **## Graph 提示詞** — 勿在本 Skill 改寫或省略步驟。
3. 可選產物如 `wiki/graph/knowledge-map.md`；必要時更新 index **Overview**；**一律** append `wiki/log.md`。
