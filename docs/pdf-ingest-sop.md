# PDF 轉譯 SOP 與命名規約

本檔為 **PDF Ingest** 的 CLI 步驟與命名 **單一來源**。Vision **怎麼寫**（RAG 轉譯、資訊圖／裝飾圖、Visual Evidence）見 [**visual-source-conversion.md**](./visual-source-conversion.md)；管線總表見 [**ingest-pipeline.md**](./ingest-pipeline.md)。

**預設路徑**：[Docling](https://github.com/docling-project/docling) 產出結構化 Markdown 初稿；**僅**頁級 triage 判定需視覺閘之頁再跑 `pdftoppm` + vision／VLM。helper：`uv run python scripts/docling-pdf.py`（模型固定於 `models/docling/`，見下方 **前置（安裝）**）。

### 本檔與 visual-source-conversion 分工

| 主題 | pdf-ingest-sop（本檔） | visual-source-conversion |
|------|------------------------|---------------------------|
| Docling、頁級 triage、`pdftoppm`、DPI、slug | **單一來源** | — |
| `<base-slug>`／`<archive-slug>` 命名 | **單一來源** | 引用本檔（資產檔名） |
| RAG 轉譯、資訊圖／裝飾圖、Agent 提示詞 | 引用 visual-source-conversion | **單一來源** |
| Visual Evidence、embed、Visual Assets | 引用 visual-source-conversion | **單一來源** |

---

## 命名三層

| 術語 | 用途 | 範例 |
|------|------|------|
| **`<base-slug>`** | 來源穩定識別名；**資產目錄名**一律用它 | `260701-金融業生成式AI平台工程-Justin` |
| **`<archive-slug>`** | `raw/sources/` 檔名與 wiki `archive_slug` | 見下方表 |
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

### 視覺資產目錄與命名（強制）

視覺資產依 **`<base-slug>` 分目錄**存放；檔名僅含頁碼，**不重複** base-slug 前綴。

```text
raw/assets/<base-slug>/p<NN>.png
```

| 層級 | 規則 | 範例 |
|------|------|------|
| **目錄** | `raw/assets/<base-slug>/`；`<base-slug>` 與原件識別名一致 | `raw/assets/260701-金融業生成式AI平台工程-Justin/` |
| **檔名** | `p` + **PDF 實際頁碼** + `.png` | `p01.png`、`p05.png` |
| **頁碼 `<NN>`** | 2 位補零（`01`…`99`）；≥100 頁用 3 位 | 第 5 頁 → `p05.png` |
| **禁止** | 扁平檔名 `<base-slug>-p05.png`、`-05.png`（缺 `p`）、未補零 `p1.png`、用 `<archive-slug>` 作目錄名 | — |

**`<base-slug>` vs `<archive-slug>`**

| 用途 | 用哪個 slug |
|------|-------------|
| `raw/assets/` **目錄名** | **`<base-slug>`**（固定，不含日期／頁面範圍） |
| `raw/sources/` 檔名、wiki `archive_slug` | **`<archive-slug>`**（可含 `-頁1至5`、`YYYYMMDD_` 前綴） |
| 部分 ingest 匯出 | 只匯出範圍內頁面，**目錄仍用 `<base-slug>`**，檔名仍用實際 PDF 頁碼（例：處理 1–5 頁 → `p01.png`…`p05.png`） |

**範例**（`base-slug = 260701-金融業生成式AI平台工程-Justin`，ingest 第 1–5 頁）：

```text
raw/assets/260701-金融業生成式AI平台工程-Justin/p01.png
raw/assets/260701-金融業生成式AI平台工程-Justin/p05.png
raw/sources/260701-金融業生成式AI平台工程-Justin-頁1至5.md
```

**匯出後重新命名**（`pdftoppm` 產出可能為 `-1.png` 或 `-01.png`）：

```bash
mkdir -p "raw/assets/<base-slug>"
# 將 <OS-temp>/<base-slug>-page-05.png → raw/assets/<base-slug>/p05.png
# （Windows／macOS／Linux：用系統暫存目錄，勿寫死 /tmp）
mv "<OS-temp>/<base-slug>-page-05.png" "raw/assets/<base-slug>/p05.png"
```

或由 helper 僅匯出視覺閘候選頁：

```bash
uv run python scripts/docling-pdf.py "<path>.pdf" --export-vision-assets
```

**各產物引用路徑**

| 產物 | embed／連結路徑（相對該檔案） |
|------|------------------------------|
| `raw/sources/<archive-slug>.md` | `../assets/<base-slug>/p<NN>.png` |
| `wiki/sources/<archive-slug>.md` | `../../raw/assets/<base-slug>/p<NN>.png` |
| `wiki/queries/*.md` | `../../raw/assets/<base-slug>/p<NN>.png` |

歸檔稿 Visual Evidence 範例：

```md
![Cloud Native AI Runtime 架構](../assets/260701-金融業生成式AI平台工程-Justin/p05.png)

- **資產**：`../assets/260701-金融業生成式AI平台工程-Justin/p05.png`
- **來源位置**：PDF 第 5 頁
```

---

## 混合管線（Docling 預設 + 視覺閘例外）

```text
PDF
 ├─ Docling（預設）→ 結構化 MD 初稿 + 表格／版面
 ├─ 頁級分流：文字／表格夠 → 整理進 raw/sources
 └─ 僅「架構圖／流程圖／對照表／文字層極短」頁
       → 匯出圖（優先 Docling 內嵌／裁切；否則 pdftoppm 整頁）+ vision（或 Docling VLM）補 Visual Evidence
```

| 類型 | 判斷 | 主路徑 |
|------|------|--------|
| **文字／表格型** | Docling／文字層段落完整，無資訊圖硬閘 | Docling 初稿 → 直接整理進 `raw/sources/` |
| **資訊圖頁** | 架構圖、流程圖、對照表、KPI；或文字層極短 | Docling 保留文字；**另** `pdftoppm` + vision／VLM |
| **掃描型** | 幾乎無可抽取文字 | Docling OCR 優先；不足再 vision；標 Limitations |

**前置（安裝）**

需已安裝 [uv](https://docs.astral.sh/uv/)。建議 Python **3.12**（`.python-version`）；範圍 `>=3.10,<3.14`。另需系統工具：`pdfinfo`／`pdftotext`／`pdftoppm`（poppler）；大圖偵測建議有 `pdfimages`。

```bash
# 1) Python 依賴（Docling／torch）
uv sync --group pdf

# 2) Docling 預設模型組 → 固定目錄 models/docling/（已 gitignore；約 1.2GB）
#    含：layout、tableformer、code_formula、picture_classifier、rapidocr
#    勿只傳 rapidocr，否則缺 layout／tableformer，轉換會失敗或重下到 ~/.cache
uv run docling-tools models download -o models/docling

# 3) 確認 helper
uv run python scripts/docling-pdf.py --help
```

| 項目 | 說明 |
|------|------|
| **模型目錄** | `models/docling/`（repo 相對；**不進 Git**） |
| **覆寫路徑** | 環境變數 `DOCLING_ARTIFACTS_PATH`（須含 `RapidOcr/`、`docling-project--docling-layout-heron/`、`docling-project--docling-models/` 等） |
| **下載來源** | RapidOCR 權重來自 **ModelScope**；layout／tableformer 等來自 **Hugging Face**（`docling-project/*`）。上游無「全部改走 HF」開關 |
| **CLI** | 請用 `uv run docling-tools ...`；直接打 `docling-tools` 常因 PATH 找不到而失敗 |

| 平台 | torch | 說明 |
|------|-------|------|
| **Intel macOS (x86_64)** | **`torch==2.2.2`**（PyTorch 最後支援版）+ `numpy<2` + `transformers<5` | **不需要 GPU**；CPU 可跑 |
| **Apple Silicon／Linux** | 可用 `torch>=2.4` | 有 GPU／MPS 會更快，非必須 |

`scripts/docling-pdf.py` 以 `artifacts_path=models/docling` 呼叫 Docling；缺模型時會提示上述下載指令。若 Docling 仍失敗，會 **自動後備** 為逐頁 `pdftotext`（stdout `engine: pdftotext-fallback`）；仍須對視覺閘頁跑 vision。

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

### 2. Docling 初稿 + 頁級分流

```bash
# 初稿 + 分流 JSON（stdout）；draft 預設寫入 <OS-temp>/<base-slug>-docling-draft.md
# （scripts/docling-pdf.py 使用 tempfile.gettempdir()，Windows 可用）
uv run python scripts/docling-pdf.py "<path>.pdf" --base-slug "<base-slug>"

# 僅看哪些頁需 vision（不跑 Docling）
uv run python scripts/docling-pdf.py "<path>.pdf" --triage-only

# 部分頁
uv run python scripts/docling-pdf.py "<path>.pdf" --page-from 1 --page-to 5
```

腳本會：

1. 以 **Docling** 產出結構化 Markdown 初稿（表格／閱讀順序優先走本機，降低雲端 vision token）。
2. 以每頁 `pdftotext` 字元數與關鍵詞做 **頁級 triage**（預設字元閾值 200）。
3. 在 stdout 印出 `vision_pages` 清單供 Agent 使用。

**文字／表格夠的頁**：以 Docling 初稿為主整理進歸檔，**不必**逐頁送雲端 vision。

### 3. 判定視覺閘（硬閘）

下列任一成立 → **必須** 匯出該頁圖並 vision／VLM（即使 Docling 已有標題）：

- 架構圖、流程圖、對照表、KPI 區塊
- 文字層極短但版面有大塊圖形（`docling-pdf` 的 `short_text`／keyword 候選）
- 掃描頁或 OCR／Docling 明顯不足

**禁止**只抄標題結案。Agent 應覆核 `vision_pages`：可剔除誤報；若漏報資訊圖頁，**手動加入**。

### 4. 匯出視覺閘頁面圖（內嵌圖優先）

預設 **144 DPI**；vision 不足時重試 **288 DPI**，並在歸檔 metadata 註明。

```bash
# 只匯出 triage 候選頁 → raw/assets/<base-slug>/p<NN>.png
# 優先 Docling 抽出／裁切頁內圖片；抽不到（常見：純向量架構圖）再整頁 pdftoppm
uv run python scripts/docling-pdf.py "<path>.pdf" --base-slug "<base-slug>" --export-vision-assets --triage-only

# 強制整頁渲染（舊行為）
uv run python scripts/docling-pdf.py "<path>.pdf" --export-vision-assets --force-page-render --triage-only

# 或手動單頁
pdftoppm -f 5 -l 5 -png -r 144 "<path>.pdf" "<OS-temp>/<base-slug>-page"
# …-05.png → raw/assets/<base-slug>/p05.png（OS-temp = tempfile.gettempdir()）
```

stdout 的 `exported_assets[].method`：

| method | 意義 |
|--------|------|
| `docling_picture` | Docling 內嵌圖或自頁面裁切的 figure |
| `pdftoppm_page` | 無可用內嵌／裁切圖（或 `--force-page-render`）→ 整頁 PNG |

`pdftoppm` 輸出檔名可能為 `-1.png` 或 `-01.png`；**重新命名時以 PDF 實際頁碼為準**。

### 5. Vision／VLM 文字化（僅候選頁）

對需視覺閘的每一頁／每一張匯出圖（品質不可縮減）：

1. **編排**：凡讀圖依 [**visual-source-conversion.md → 平行 Vision 編排**](./visual-source-conversion.md#平行-vision-編排強制凡讀圖) — **每張圖派 subagent**（多張平行；同時 3–5、每員 1–2 張）；主 Agent **禁止**自行 `Read` 圖片。
2. **讀圖（subagent）**：子代理打開對應 `raw/assets/<base-slug>/p<NN>.png`（或整頁匯出圖）。
3. **套用提示詞**：完整複製 [**visual-source-conversion.md → Agent 用提示詞（強制）**](./visual-source-conversion.md#agent-用提示詞強制可複製) 執行轉寫（勿改寫成摘要版提示）。Subagent 須回傳該檔規定的 **VE schema 區塊**（勿寫整份歸檔）。
4. **合併就地**：主 Agent 將各區塊寫入 `raw/sources/` **該頁／該節正下方**（embed、層／節點盤點、主要資料流 `→`）。**禁止**先寫完全文再把所有圖堆到文末 `## Visual Evidence`（見 [放置規則](./visual-source-conversion.md#放置規則強制歸檔稿)）。
5. 衝突時以圖為準，標 `（推測）`／`（未知）`。
6. 跑 `python3 scripts/wiki-lint.py`；出現 `weak Visual Evidence` 或 `Visual Evidence dumped at end` 則未完成。

可選：本機 Docling VLM 僅作輔助；最終文字仍須符合上述提示詞與硬閘。

### 6. 寫入歸檔稿

合併 **Docling 初稿**（文字／表格頁）與 **vision 補寫**（資訊圖頁），新增 `raw/sources/<archive-slug>.md`（詳盡還原，非 wiki 摘要）。文首建議含：

```md
## 來源資訊

- base-slug：`<base-slug>`
- archive-slug：`<archive-slug>`
- 原件：`../originals/<檔名>.pdf`
- 頁面範圍：第 1–5 頁（全檔共 14 頁）／或「全檔」
- 原件 SHA-256：`…`
- 轉檔：Docling（結構化 MD 初稿）
- 視覺閘頁：`[5, 6, 8, 12]`（pdftoppm -png -r 144 + vision）
- triage：文字／表格頁直入；資訊圖頁視覺閘已適用／未適用
```

部分 ingest **必須** 在 `## Limitations / Gaps` 註明未涵蓋頁碼。

### 7. 後續 wiki 步驟

依 [PROMPTS.md](./PROMPTS.md) § Ingest 步驟 7–13：`wiki/sources/` 摘要（含 **`## Visual Assets`** 與原圖 embed）、`concepts`／`entities`、連結、index、**輸入原件清理**（`scripts/ingest-cleanup.py`）、log。

---

## 品質驗收清單

完成 PDF ingest 前確認：

- [ ] 原件已入 `raw/originals/`，且 SHA-256 已記錄
- [ ] 已跑 `scripts/docling-pdf.py`（或同等 Docling 轉檔）並保留／合併初稿
- [ ] 每個處理頁有 `### 第 N 頁`（或等效分節）
- [ ] 非視覺閘頁未無謂送雲端 vision
- [ ] 視覺閘頁資產在 `raw/assets/<base-slug>/p<NN>.png`，且有 Visual Evidence + `![]()` embed，且 **就地**放在該頁／該節下（非文末總庫）
- [ ] 視覺閘已採 **讀圖一律 subagent**（多張平行），log 註明 `vision_via: subagent`
- [ ] `wiki/sources/*` 含 **`## Visual Assets`**（有資訊圖時），embed 路徑正確
- [ ] 架構圖／對照表已表格化或層級盤點，非僅標題
- [ ] 符合 [visual-source-conversion.md → Vision 文字化原則](./visual-source-conversion.md#vision-文字化原則rag-導向)
- [ ] `wiki-lint` 無 `weak Visual Evidence`／`Visual Evidence dumped at end`
- [ ] 部分 ingest 已標未涵蓋頁
- [ ] `archive_slug` 使用 `<archive-slug>`，與 `raw/sources/` 檔名一致；`sources[].resource` 指向該歸檔稿
- [ ] 輸入原件已於歸檔成功後清理（步驟 12）

---

## 常見錯誤

| 錯誤 | 正確做法 |
|------|----------|
| 全檔每頁都送雲端 vision | Docling 預設；僅 `vision_pages`／硬閘頁 vision |
| 有架構圖卻只採用 Docling 標題 | 該頁進視覺閘，補層級表 + Visual Evidence |
| 資產扁平檔名 `<base-slug>-p05.png` | 目錄 `raw/assets/<base-slug>/p05.png` |
| 目錄用 `<archive-slug>` | 目錄一律 `<base-slug>` |
| 頁碼未補零 `p1.png` | `p01.png`（2 位補零） |
| 第 4 頁圖檔卻標「第 5 頁」 | 檔名、來源位置、正文三者頁碼一致 |
| 描述「藍色方塊」「現代感設計」 | 見 visual-source-conversion → Vision 文字化原則 |
| 部分 ingest 卻用全檔 `<archive-slug>` | slug 加 `-頁<start>至<end>` |
| 把 wiki 摘要貼進 `raw/sources/` | 歸檔詳盡、wiki 摘要分離 |
| 未安裝 docling／相容 torch 就略過轉檔 | `uv sync --group pdf`（Intel Mac 勿強裝 torch≥2.4；見 `pyproject.toml`） |
| 只下 RapidOCR、缺 layout／tableformer | 下完整預設組：`uv run docling-tools models download -o models/docling`（勿只傳 `rapidocr`） |
| RapidOCR／Docling 模型找不到／又下載到 `~/.cache` | 固定目錄同上；helper 預設讀 `models/docling/`（`DOCLING_ARTIFACTS_PATH` 可覆寫） |
| 圖拆得出來但 Visual Evidence 空殼 | **Agent 必須逐張讀圖**寫層／節點＋資料流；禁止「細節以原圖為準」。`wiki-lint` 會對 canonical 歸檔報 `weak Visual Evidence` |
| 全文寫完再把所有圖堆在文末 `## Visual Evidence` | **就地**寫在該頁／該節下；`wiki-lint` 報 `Visual Evidence dumped at end` |
| 主 Agent 自行 `Read` 圖片做 Vision | **一律**派 subagent 讀圖（見 visual-source-conversion → 平行 Vision 編排） |
| 缺頁／空殼仍繼續合併 | 合併前驗收閘失敗須 **自動重派**（同圖最多再 2 次）；見 visual-source-conversion → 主 Agent 合併規則 |
| 硬編碼 `/tmp/...`（Windows 失敗） | `scripts/docling-pdf.py` 使用 `tempfile.gettempdir()` |

---

## 相關文件

- [visual-source-conversion.md](./visual-source-conversion.md) — 視覺硬閘、Visual Evidence 格式
- [ingest-pipeline.md](./ingest-pipeline.md) — 13 步管線
- [okf.md](./okf.md) — `archive_slug` 與 resource 語意
- [Docling](https://github.com/docling-project/docling) — 本機文件解析
