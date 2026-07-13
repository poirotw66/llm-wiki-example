# 視覺來源轉換（Visual Source Conversion）

當 Ingest triage 判定來源含 **資訊性視覺**（流程圖、架構圖、截圖、掃描頁、ER、簡報圖、表格圖等），**必須** 在寫入 `raw/sources/` 前依本檔處理。  
使用者只需說「Ingest 這個檔」或將檔案置於 `raw/inbox/`，**無須** 另下視覺轉換指令。

規約見 [AGENTS.md](../AGENTS.md) → **來源轉換政策**；管線步驟見 [ingest-pipeline.md](./ingest-pipeline.md)。**PDF** 專用步驟與資產命名見 [**pdf-ingest-sop.md**](./pdf-ingest-sop.md)。

---

## `raw/sources/` 與 `wiki/sources/` 分工

| 路徑 | 目的 | 寫法 |
|------|------|------|
| **`raw/sources/<slug>.md`** | 可追溯 **canonical 歸檔稿** | **盡可能詳盡還原**；允許長文 |
| **`wiki/sources/<slug>.md`** | OKF **來源摘要頁** | 3–5 bullets Summary 等；**從歸檔稿抽取** |

**歸檔稿不是 wiki 草稿**。不得因「wiki 要簡潔」而把 `raw/sources/` 寫成精簡版。

### 歸檔稿應包含（能還原則盡量還原）

- **逐頁結構**：`### Slide N` 或 `### 第 N 頁`；每頁下寫可見標題、正文、列表、表格儲格。
- **OCR／文字層**：PDF 可抽取文字盡量保留（含頁碼標記 `N`）。
- **圖內資訊進正文**：架構圖的層級、節點名、箭頭關係、表格欄列；流程圖的決策菱形與分支標籤。
- **Visual Evidence**：每頁有圖時對應一節；含資產路徑、關係概要、層／節點盤點。
- **不確定性標記**：（確定）／（推測）／（未知）。

### 禁止

- 全簡報只寫一段 Summary 或每頁一句話
- 有架構圖卻只寫「平台定位」不寫元件
- 把 `wiki/sources/` 的摘要貼進 `raw/sources/` 當作歸檔完成

---

## 何時觸發

| 觸發 | 範例 |
|------|------|
| 獨立圖片檔 | `.png`、`.jpg` 規格截圖 |
| 文件內嵌圖 | PDF／PPTX 內之圖表、投影片 |
| 掃描頁 | 無法直接複製文字之 PDF 頁 |

若 triage 判定 **無** 資訊性視覺，在 log 或歸檔稿註明「視覺轉換閘：未適用」即可。

---

## 產出要求

1. **萃取資產** — 可辨識之圖寫入 `raw/assets/`。命名見 [**pdf-ingest-sop.md**](./pdf-ingest-sop.md)：**`<base-slug>-p<NN>.png`**（`<NN>` 為 PDF／簡報**實際頁碼**；資產一律用 `<base-slug>`，不用 `<archive-slug>`）。
2. **Visual Evidence Block** — 在 `raw/sources/<slug>.md` 內以結構化區塊記錄視覺內容文字化結果。
3. **不確定性** — 無法辨識處標 `（未知）`；推測處標 `（推測）`。
4. **Limitations** — 在來源頁 `## Limitations / Gaps` 列出無法讀取之圖、模糊欄位。

### 硬閘（階段 1 必過）

下列任一成立時，**不得**僅寫標題／口號即結案：

| 訊號 | 強制動作 |
|------|----------|
| 內容含 **架構圖／流程圖／對照表／KPI 區塊** | 匯出 **該頁整頁（或裁切圖）** 至 `raw/assets/`，並用 vision／人工對圖文字化 |
| PDF／簡報頁 **文字層極短**（例如僅標題），但頁面有大塊圖形 | 視為「資訊在圖內」；必須 vision 讀圖後再寫入 Slide Notes＋Visual Evidence |
| 圖內有層級、節點、箭頭、表格 | Visual Evidence 至少含：**層／節點清單**、**主要資料流／控制流**、**資產路徑**、**來源頁碼** |

**禁止**：

- 只抄 OCR／文字層標題，略過圖內元件名稱
- 資產檔頁碼與「來源位置」標註不一致（例：內容是第 4 頁圖，卻標成第 5 頁）
- 以「解析度不足」略過尚未用更高解析度重匯出嘗試的頁面

---

## Visual Evidence Block 格式（建議）

```md
## Visual Evidence

### [圖1] <簡短標題>

- **資產**：../assets/<base-slug>-p05.png
- **來源位置**：PDF 第 5 頁
- **關係概要**：（確定）A → B → C……
- **層／節點盤點**：（確定）用表格或 bullet 列出圖中可見標籤
- **限制**：（未知）／（推測）……
```

若頁面是 **架構圖**，Slide Notes 對應節亦應含「架構層級盤點」表，不得只寫一句定位標語。

wiki 來源頁 `wiki/sources/<slug>.md` 可摘要引用上述內容，並連結歸檔稿。

---

## 無法讀取時

- **保留** 原件於 `raw/originals/`（若適用）與可匯出之 `raw/assets/`。
- **勿** 虛構圖中文字或關係。
- 在 **Limitations / Gaps** 說明缺口；wiki 敘述僅寫可驗證部分。

---

## 階段 1 實作方式

由 **Agent**（Cursor 等）執行 vision／手動轉述，無需外掛 CLI。  
階段 2 可選評估 Graphify 等工具協助 **抽取草稿**，但 **OKF wiki 定稿** 仍須經本 Ingest 管線與引用規則。
