---
name: llm-wiki-ingest
description: LLM Wiki Ingest。使用者輸入 /ingest、ingest、歸檔、收斂來源、納入 wiki 時使用。含多模態 triage／轉檔（見 docs/ingest-pipeline.md；視覺硬閘見 docs/visual-source-conversion.md）；步驟見 docs/PROMPTS.md；規約見 AGENTS.md。
---

# /ingest

## 觸發

`/ingest`、`ingest`、歸檔、Ingest、收斂來源、納入 wiki

## 執行

1. 遵循工作區根目錄 **AGENTS.md**（含 **操作：Ingest**、硬約束、`raw/` 不可變）。
2. **依全文執行** 工作區根目錄 **docs/PROMPTS.md** 的 **## Ingest 提示詞** — 勿在本 Skill 改寫或省略步驟。
3. 完成後確認 `wiki/index.md` 已更新（若適用）、`wiki/log.md` 已 append。

## `raw/sources/` vs `wiki/`（強制）

| 產物 | 粒度 | 禁止 |
|------|------|------|
| **`raw/sources/<slug>.md`** | **盡可能詳盡還原**（canonical 歸檔稿） | 用 wiki 級摘要、幾句標語或「Slide Notes 精簡版」代替 |
| **`wiki/sources/*`** | **摘要**（OKF 來源頁 Schema） | 把整份投影片逐頁抄進 wiki 頁 |

**歸檔稿必須**（見 **docs/visual-source-conversion.md**）：

- **逐頁／逐段**還原：簡報每張投影片一節；PDF 保留可抽取文字層與頁碼標記。
- **圖內資訊寫入正文**：架構圖、流程圖、對照表、KPI 區塊須 vision 文字化（層／節點、箭頭、表格儲格），不可只寫標題。
- **Visual Evidence**：每頁有資訊性視覺時須有對應區塊；資產 `raw/assets/<slug>-<頁碼>.png` 頁碼須一致。
- **可長**：歸檔稿允許遠長於 `wiki/sources/`；修訂時 **另建新檔**（如 `YYYYMMDD_<slug>.md`），勿改寫既有 `raw/`。

**wiki 頁**從歸檔稿 **抽取摘要**；若使用者抱怨「歸檔太簡」，優先 **補厚 `raw/sources/`**，而非只改 wiki 一句話。

## 使用者輸入

訊息中的檔案路徑、URL 或貼上內容為本次 **指定來源**。未提供時請向使用者索取。
