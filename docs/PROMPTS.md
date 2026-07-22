# Operations Prompts（複製貼上）

Ingest／Query／Lint／FAQ／Graph 之標準提示詞。規約見 [**AGENTS.md**](../AGENTS.md)。日誌：每次操作須 append `wiki/log.md`（無檔案變更時用 **pass** 或 **no-op**）。若操作新增／刪除／實質變更 wiki 頁或目錄所列產物，更新 `wiki/index.md`。

**Cursor**：可用薄 Skill `/ingest`、`/query`、`/lint`、`/faq`、`/graph`（定義見 [`skills/`](../skills/)；以 `npx skills add` 安裝，見 [README](../README.md#cursor-skill-用法)）觸發；Skill 委派本檔對應章節，**勿在 Skill 內複製步驟**。`.cursor/` 為本機可選副本，**不進 Git**。

---

## Ingest 提示詞

將本 repository 作為以來源為根據的 wiki 系統。完整對照表見 [**docs/ingest-pipeline.md**](./ingest-pipeline.md)。

嚴格遵循 **AGENTS.md** → **操作：Ingest**（13 步）：

1. 讀取指定來源（路徑、`raw/inbox/` 或批次）；未提供時向使用者索取。
2. **Detect／Triage**：副檔名、是否需轉 Markdown、是否含資訊性視覺（見 ingest-pipeline 支援類型表）。
3. 必要時轉為結構化 Markdown。**PDF** 依 [**docs/pdf-ingest-sop.md**](./pdf-ingest-sop.md)：**Docling 預設**（`python scripts/docling-pdf.py`）→ 結構化 MD 初稿；頁級分流後，文字／表格夠則直入歸檔；**僅**架構圖／流程圖／對照表／文字層極短頁再 `pdftoppm` + vision／VLM（資產 **`raw/assets/<base-slug>/p<NN>.png`**）。含視覺則依 [**docs/visual-source-conversion.md**](./visual-source-conversion.md)。**硬閘**：資訊圖頁禁止只抄標題；須寫「層／節點盤點」+ Visual Evidence；資產頁碼須與來源標註一致。
4. 非 Markdown 原件歸檔 `raw/originals/`（新檔；勿改寫既有 `raw/` 檔）。
5. 視覺資產寫入 `raw/assets/`（若適用；PDF 命名見 **pdf-ingest-sop.md**）。
6. **新增** canonical 歸檔 `raw/sources/<archive-slug>.md`（僅新檔；`<archive-slug>` 見 **pdf-ingest-sop.md**／**okf.md**；修訂另建新檔）。**歸檔稿須盡可能詳盡還原原文，非精簡版**：合併 Docling 初稿與視覺閘補寫；逐頁／逐段；文字／表格頁以 Docling 為主；**資訊圖頁**須 vision／VLM 寫入正文＋Visual Evidence（含 `![]()` embed 原圖）；**禁止**僅抄標題或幾句摘要；歸檔稿可遠長於 wiki 摘要頁。
7. 依歸檔稿建立或更新 `wiki/sources/*`（**摘要**，非歸檔全文複製），區塊標題須符合 **來源頁 Schema**（含 **`## Visual Assets`**：有資訊性視覺時 **必須** `![]()` embed `../../raw/assets/<base-slug>/p<NN>.png`）。版型：`docs/templates/page-template-source.md`。
8. 抽取並更新 `wiki/concepts/*`、`wiki/entities/*`。
9. 更新相關頁；建立雙向連結（**markdown 相對路徑**；勿用 `/path.md`）。
10. 每個新建或更新的 **Concept** frontmatter 補齊 **OKF v0.1 建議欄位**：`description`、`resource`（**歸檔 slug** 如 `my-api-intro` → `raw/sources/my-api-intro.md`，或 **HTTPS URL**）、`timestamp`（ISO 8601）；對照 [**docs/okf.md**](./okf.md) → **resource 語意**。
11. 更新 `wiki/index.md`。
12. **輸入原件清理**：步驟 4（非 MD）與步驟 6（MD 直達歸檔）成功後，若輸入路徑在 `raw/inbox/`、repo 根目錄等**非** `raw/originals/`／`raw/sources/`／`raw/assets/` 位置，執行 `python scripts/ingest-cleanup.py "<input-path>" --archive "<archive-path>" [--archive "<archive-path>"]` 刪除輸入副本。**禁止**刪 `raw/` 歸檔本體。
13. Append `wiki/log.md`（含 triage／轉檔摘要，或註明視覺閘未適用；步驟 12 有刪檔時註明路徑）。

所有可驗證主張須引用來源；不確定時標記（`（推測）`、`（未知）`）；有根據的主張不需另加標記。

---

## Query 提示詞

以可追溯、以來源為根據的流程回答使用者問題。

依序：
1. 先查 `wiki/` 摘要頁（`faq`、`concepts`、`entities`、`queries`）；優先讀來源頁 **`## Visual Assets`**。
2. 摘要足夠且無衝突 → 直接回答。
3. 不足、模糊或衝突 → 核對 `raw/sources/*`（含 **Visual Evidence** 與 `raw/assets/`）。
4. 答案須含可追溯位置（至少檔案路徑；必要時章節／行）。
5. 引用來源；不確定時標記（`（推測）`、`（未知）`）；有根據的主張不需另加標記。
6. **視覺答案（強制）**：若問題涉及架構圖、流程圖、對照表等資訊性視覺，答案 **必須** 附上對應 `raw/assets/` 原圖的 Markdown embed（自當前回答脈絡選路徑：聊天中引用 wiki 頁時用 `../../raw/assets/<base-slug>/p<NN>.png` 或連至含 embed 的 [來源頁](../sources/....md)），並標明 PDF／投影片頁碼。**禁止**只描述圖內容而不給原圖。
7. 若可重用，持久化至 `wiki/queries/*` 並更新 `wiki/index.md`（**Queries** 區：連結 + 一行說明）；持久化答案亦須保留步驟 6 的 embed。
8. **一律** append `wiki/log.md` — 含僅回答、未持久化（記 **pass** 或 **no-op**，見下方 **Wiki log append**）。

---

## Lint 提示詞

執行 wiki 品質 Lint，附證據回報。

遵循 **AGENTS.md** → **操作：Lint**。

1. **先執行** `python scripts/wiki-lint.py`；依 stderr 修正後重跑至 exit 0。
2. 再執行 Agent 深度檢查（見下方清單）。

檢查：矛盾、過時資訊、孤兒頁、缺頁、重複概念、無來源頁、過時頁面、**斷鏈**（相對路徑目標不存在）、**`/path.md` 根路徑**（嵌於 repo 時必斷）、**`[[...]]` 混用**（見 **AGENTS.md** → 連結規則）、**視覺資產缺口**（`raw/assets/<base-slug>/` 有圖但對應 `wiki/sources/*` 缺 **`## Visual Assets`** 或缺 `![]()` embed；或 embed 路徑與 `raw/assets/<base-slug>/p<NN>.png` 不一致）。

結果輸出至 `wiki/lint/`，附可執行修正與檔案級引用。**新增或實質變更** lint 產物時，若目錄需露出，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）。

**一律** append `wiki/log.md`（即使未寫新 lint 檔）：一行摘要，例如 `pass`、`no issues` 或簡短發現。

---

## FAQ 提示詞

自既有 wiki 產出可重用 FAQ。

遵循 **AGENTS.md** → **操作：FAQ**、**FAQ 頁格式**、**FAQ 規則**。

**空 wiki**：若 `wiki/` 尚無可掃描的 Concept 頁（僅 `index.md`、`log.md` 或各子目錄為空），**勿虛構題目**、勿寫入 `wiki/faq/`；向使用者說明須先 Ingest，並 append `wiki/log.md` 記 **no-op**。

1. 讀取 `wiki/index.md`。
2. 掃描 sources、concepts、entities、queries。
3. 偵測重複模式、易混淆主題、流程、跨頁關係。
4. 產出 8–15 題（初階至進階，至少一題跨頁綜合）。勿虛構 wiki 無依據的題目。
5. 持久化至 `wiki/faq/`，使用規定 frontmatter 與 Scope／FAQ／Short Answer／Detailed Answer／Related Pages 結構。
6. 更新 `wiki/index.md`（FAQ 區：連結 + 一行說明）。
7. Append `wiki/log.md`。

---

## Graph 提示詞

建立或更新本 wiki 知識關係。

遵循 **AGENTS.md** → **操作：Graph**。

**空 wiki**：若尚無 Concept 頁可遍歷，**勿**產出 `wiki/graph/*`；向使用者說明須先累積知識頁，並 append `wiki/log.md` 記 **no-op**（或 **pass**）。

1. 遍歷 wiki 頁（遵守連結與關係規則）。
2. 抽取連結並適當推論關係。
3. 產出或更新 graph 摘要（可選：`wiki/graph/knowledge-map.md`）。
4. **新增或實質變更** graph 產物時，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）。
5. **一律** append `wiki/log.md` — 含可選輸出或 **未變更**（記 `pass`、`no-op` 或一行摘要）。

---

## Wiki log append（pass／no-op）

**AGENTS.md** 任一操作在 **無須改檔** 但仍須留痕時使用。

1. 以 `## [YYYY-MM-DD] <operation> | <title>` 格式 append 至 `wiki/log.md`。
2. 一至兩條 bullet：標 **pass**、**no-op** 或簡述結果。
3. 勿改寫或刪除既有 log 章節。

---

## 範例指令

```md
- /ingest <路徑>（或 Cursor 薄 Skill；步驟見本檔 Ingest 提示詞）
- /ingest raw/inbox/某規格.pdf
- Ingest：指定路徑 → triage → raw/sources/*.md → wiki（用上方 Ingest 提示詞）
- Ingest raw/sources/ 下既有檔（每檔一輪；更新 index + log）
- 自現有 wiki 產生 FAQ（8–15 題、勿虛構；用 FAQ 提示詞）
- 回答：<問題>（附引用與不確定性；用 Query 提示詞）
- Lint wiki（用 Lint 提示詞）
- 建立知識 graph（例如 wiki/graph/knowledge-map.md；用 Graph 提示詞）
```
