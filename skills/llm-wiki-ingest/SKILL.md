---
name: llm-wiki-ingest
description: LLM Wiki Ingest。使用者輸入 /ingest、ingest、歸檔、收斂來源、納入 wiki 時使用。含多模態 triage／轉檔（見 docs/ingest-pipeline.md；PDF 見 docs/pdf-ingest-sop.md；視覺硬閘見 docs/visual-source-conversion.md）；步驟見 docs/PROMPTS.md；規約見 AGENTS.md。
---

# /ingest

## 觸發

`/ingest`、`ingest`、歸檔、Ingest、收斂來源、納入 wiki

## 執行

1. 遵循工作區根目錄 **AGENTS.md**（含 **操作：Ingest**、硬約束、`raw/` 不可變）。
2. **依全文執行** 工作區根目錄 **docs/PROMPTS.md** 的 **## Ingest 提示詞** — 勿在本 Skill 改寫或省略步驟。
3. 操作一開始以本次 log title 執行 `python3 scripts/wiki-usage.py start ingest --title "<title>"`；完成後確認 `wiki/index.md` 已更新（若適用）、輸入原件已清理（步驟 12）、`wiki/log.md` 已 append，並執行 `python3 scripts/wiki-usage.py finish ingest --title "<title>"`。若漏掉 start，finish 會自動復原量測且拒絕 0 token。

## `raw/sources/` vs `wiki/`（強制）

| 產物 | 粒度 | 禁止 |
|------|------|------|
| **`raw/sources/<archive-slug>.md`** | **盡可能詳盡還原**（canonical 歸檔稿） | 用 wiki 級摘要、幾句標語或「Slide Notes 精簡版」代替 |
| **`wiki/sources/*`** | **摘要**（OKF 來源頁 Schema） | 把整份投影片逐頁抄進 wiki 頁 |

**歸檔稿必須**（見 **docs/visual-source-conversion.md**）：

- **逐頁／逐段**還原：簡報每張投影片一節；PDF 保留可抽取文字層與頁碼標記。
- **圖內資訊寫入正文**：架構圖、流程圖、對照表、KPI 區塊須 vision 文字化（層／節點、箭頭、表格儲格），不可只寫標題。
- **Visual Evidence**：**就地**寫在該頁／該節出現處正下方（見 **docs/visual-source-conversion.md → 放置規則**）；資產 **`raw/assets/<base-slug>/p<NN>.png`**（見 **docs/pdf-ingest-sop.md**），頁碼須一致；歸檔稿與 **`wiki/sources/*` 的 `## Visual Assets`** 須 **`![]()` embed 原圖**。**必須逐張讀圖**，並完整套用 **Agent 用提示詞（強制）**；禁止「細節以原圖為準」等空殼；**禁止**文末單一 `## Visual Evidence` 彙整所有圖。**讀圖一律 subagent**：依 **docs/visual-source-conversion.md → 平行 Vision 編排**（每張圖派 subagent；多張平行同時 3–5、每員 1–2 張、只回傳 VE schema；主 Agent **禁止**自行 `Read` 圖片，只合併）。Ingest 結束前 `wiki-lint` 不得出現 `weak Visual Evidence` 或 `Visual Evidence dumped at end`。
- **可長**：歸檔稿允許遠長於 `wiki/sources/`；修訂時 **另建新檔**（如 `YYYYMMDD_<base-slug>.md`），勿改寫既有 `raw/`。

## PDF

依 **docs/pdf-ingest-sop.md**（含 **前置（安裝）**：`uv sync --group pdf` + `uv run docling-tools models download -o models/docling`）。**Docling 預設**（`uv run python scripts/docling-pdf.py`，模型在 `models/docling/`）→ MD 初稿 + 頁級分流；文字／表格頁直入歸檔；**僅**架構／流程／對照／短文字頁再 `pdftoppm` + vision／VLM。`<base-slug>` 與 `<archive-slug>` 分工見該檔。

**wiki 頁**從歸檔稿 **抽取摘要**；若使用者抱怨「歸檔太簡」，優先 **補厚 `raw/sources/`**，而非只改 wiki 一句話。

## 使用者輸入

訊息中的檔案路徑、URL 或貼上內容為本次 **指定來源**。未提供時請向使用者索取。
