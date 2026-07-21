# PDF 轉譯 SOP 與命名規約

本檔為 **PDF Ingest** 的 CLI 步驟與命名 **單一來源**。Vision **怎麼寫**（RAG 轉譯、資訊圖／裝飾圖、Visual Evidence）見 [**visual-source-conversion.md**](./visual-source-conversion.md)；管線總表見 [**ingest-pipeline.md**](./ingest-pipeline.md)。

### 本檔與 visual-source-conversion 分工

| 主題 | pdf-ingest-sop（本檔） | visual-source-conversion |
|------|------------------------|---------------------------|
| pdfinfo、pdftotext、pdftoppm、DPI | **單一來源** | — |
| `<base-slug>`／`<archive-slug>` 命名 | **單一來源** | 引用本檔（資產檔名） |
| RAG 轉譯、資訊圖／裝飾圖、Agent 提示詞 | 引用 visual-source-conversion | **單一來源** |
| Visual Evidence、embed、Visual Assets | 引用 visual-source-conversion | **單一來源** |

---

## 命名三層

| 術語 | 用途 | 範例 |
|------|------|------|
| **`<base-slug>`** | 來源穩定識別名；**資產檔名**一律用它 | `260701-金融業生成式AI平台工程-Justin` |
| **`<archive-slug>`** | `raw/sources/` 與 wiki `resource` 的歸檔 slug | 見下方表 |
| **頁碼 `<NN>`** | PDF **實際頁碼**（非投影片邏輯序的重新編號） | 第 5 頁 → `05` |

### `<archive-slug>` 規則

| 情境 | `<archive-slug>` | 對應檔案 |
|------|------------------|----------|
| 全檔首次 ingest | `<base-slug>` | `raw/sources/<base-slug>.md` |
| **部分頁** ingest（例：1–5 頁） | `<base-slug>-頁<start>至<end>` | `raw/sources/<base-slug>-頁1至5.md` |
| 全檔修訂 | `YYYYMMDD_<base-slug>` | `raw/sources/20260713_<base-slug>.md` |
| 部分頁修訂 | `YYYYMMDD_<base-slug>-頁<start>至<end>` | `raw/sources/20260713_<base-slug>-頁1至5.md` |

* `<base-slug>` 取自原件檔名（去副檔名）或團隊約定識別名；**勿**含日期前綴或頁面範圍。
* 修訂時 **另建新檔**；勿改寫既有 `raw/` 檔。

### 視覺資產命名（強制）

```text
raw/assets/<base-slug>-p<NN>.png
```

| 規則 | 說明 |
|------|------|
| 前綴 | 一律 **`<base-slug>`**，**不是** `<archive-slug>` |
| 頁碼 | `-p` + **實際 PDF 頁碼**；2 位補零（`01`…`99`），≥100 頁用 3 位 |
| 禁止 | `-頁1至5-05`、`-05`（缺 `p`）、用投影片序號取代 PDF 頁碼 |
| 部分 ingest | 只匯出範圍內頁面，檔名仍用實際頁碼（例：處理 1–5 頁 → `-p01`…`-p05`） |

**範例**（`base-slug = 260701-金融業生成式AI平台工程-Justin`，ingest 第 1–5 頁）：

```text
raw/assets/260701-金融業生成式AI平台工程-Justin-p01.png
raw/assets/260701-金融業生成式AI平台工程-Justin-p05.png
raw/sources/260701-金融業生成式AI平台工程-Justin-頁1至5.md
```

歸檔稿內引用：

```md
- **資產**：../assets/260701-金融業生成式AI平台工程-Justin-p05.png
- **來源位置**：PDF 第 5 頁
```

---

## PDF 類型分流（Triage）

| 類型 | 判斷 | 主路徑 |
|------|------|--------|
| **文字型** | `pdftotext` 可抽出完整段落 | 文字層為主；有圖表仍走視覺閘 |
| **簡報型** | 每頁一屏、文字層短、大圖多 | 逐頁匯出 + vision（本 SOP 預設） |
| **掃描型** | 幾乎無可抽取文字 | 逐頁匯出 + OCR／vision；標 Limitations |

---

## 標準作業程序（階段 1）

使用者指定 **全檔** 或 **頁面範圍**（例：`ingest 此 PDF 第 1–5 頁`）。未指定範圍則處理全檔。

### 1. 偵測與原件歸檔

```bash
pdfinfo "<path>.pdf"
shasum -a 256 "<path>.pdf"
cp "<path>.pdf" "raw/originals/<原件檔名>.pdf"
```

記錄：總頁數、PDF 版本、SHA-256。

### 2. 抽出文字層

全檔：

```bash
pdftotext -layout "<path>.pdf" -
```

部分頁（例：1–5）：

```bash
pdftotext -f 1 -l 5 -layout "<path>.pdf" -
```

保留 `-layout` 輸出；歸檔稿以 `### 第 N 頁` 分節，並保留可見頁碼標記。

### 3. 判定每頁是否需視覺閘

下列任一成立 → **必須** 匯出該頁圖並 vision：

- 架構圖、流程圖、對照表、KPI 區塊
- 文字層極短但版面有大塊圖形
- 掃描頁或 OCR 明顯不足

### 4. 匯出頁面圖（≥2×）

預設 **144 DPI**；vision 不足時重試 **288 DPI**，並在歸檔 metadata 註明。

單頁：

```bash
pdftoppm -f 5 -l 5 -png -r 144 "<path>.pdf" "/tmp/<base-slug>-page"
# 產出 …-05.png → 重新命名為 raw/assets/<base-slug>-p05.png
```

範圍（例：1–5）：

```bash
pdftoppm -f 1 -l 5 -png -r 144 "<path>.pdf" "/tmp/<base-slug>-page"
# …-01.png …-05.png → raw/assets/<base-slug>-p01.png …-p05.png
```

`pdftoppm` 輸出檔名可能為 `-1.png` 或 `-01.png`；**重新命名時以 PDF 實際頁碼為準**，對齊 `<base-slug>-p<NN>.png`。

### 5. Vision 文字化（逐頁轉譯）

對需視覺閘的每一頁，依 [**visual-source-conversion.md** → **Vision 文字化原則（RAG 導向）**](./visual-source-conversion.md#vision-文字化原則rag-導向) 執行：

1. 讀匯出圖與同頁 `pdftotext` 文字層（文字層作初稿，**不以文字層單獨結案**）。
2. 將**資訊圖**轉為結構化 Markdown；**忽略裝飾圖**（見 visual-source-conversion）。
3. 撰寫 Visual Evidence；**每節須含 `![]()` embed 原圖**。
4. 衝突時以圖為準，標 `（確定）`／`（推測）`／`（未知）`。

### 6. 寫入歸檔稿

新增 `raw/sources/<archive-slug>.md`（詳盡還原，非 wiki 摘要）。文首建議含：

```md
## 來源資訊

- base-slug：`<base-slug>`
- archive-slug：`<archive-slug>`
- 原件：`../originals/<檔名>.pdf`
- 頁面範圍：第 1–5 頁（全檔共 14 頁）／或「全檔」
- 原件 SHA-256：`…`
- 文字層：pdftotext -layout
- 頁面匯出：pdftoppm -png -r 144（或 288）
- triage：簡報型 PDF；視覺轉換閘：已適用／未適用
```

部分 ingest **必須** 在 `## Limitations / Gaps` 註明未涵蓋頁碼。

### 7. 後續 wiki 步驟

依 [PROMPTS.md](./PROMPTS.md) § Ingest 步驟 7–12：`wiki/sources/` 摘要（含 **`## Visual Assets`** 與原圖 embed）、`concepts`／`entities`、連結、index、log。

---

## 品質驗收清單

完成 PDF ingest 前確認：

- [ ] 原件已入 `raw/originals/`，且 SHA-256 已記錄
- [ ] 每個處理頁有 `### 第 N 頁` 節
- [ ] 資產檔名為 `<base-slug>-p<NN>.png`，且 `NN` 與「來源位置」一致
- [ ] 有資訊性視覺的頁面皆有 Visual Evidence，且歸檔稿內有 `![]()` embed
- [ ] `wiki/sources/*` 含 **`## Visual Assets`**，embed 路徑為 `../../raw/assets/<base-slug>-p<NN>.png`
- [ ] 架構圖／對照表已表格化或層級盤點，非僅標題
- [ ] 符合 [visual-source-conversion.md → Vision 文字化原則](./visual-source-conversion.md#vision-文字化原則rag-導向)（無配色噪音、裝飾圖未寫入、表格完整）
- [ ] 部分 ingest 已標未涵蓋頁
- [ ] `resource` 使用 `<archive-slug>`，與 `raw/sources/` 檔名一致

---

## 常見錯誤

| 錯誤 | 正確做法 |
|------|----------|
| 資產用 `<archive-slug>-p05` | 資產一律 `<base-slug>-p05` |
| 第 4 頁圖檔卻標「第 5 頁」 | 檔名、來源位置、正文三者頁碼一致 |
| 架構頁只抄標題 | vision 後補層級表 + 資料流 + Visual Evidence（見 visual-source-conversion） |
| 描述「藍色方塊」「現代感設計」 | 見 visual-source-conversion → Vision 文字化原則 |
| 部分 ingest 卻用全檔 `<archive-slug>` | slug 加 `-頁<start>至<end>` |
| 把 wiki 摘要貼進 `raw/sources/` | 歸檔詳盡、wiki 摘要分離 |

---

## 相關文件

- [visual-source-conversion.md](./visual-source-conversion.md) — 視覺硬閘、Visual Evidence 格式
- [ingest-pipeline.md](./ingest-pipeline.md) — 12 步管線
- [okf.md](./okf.md) — `resource` slug 語意
