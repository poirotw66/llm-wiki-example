# Ingest 管線（階段 1：多模態合併版）

本檔為 **Ingest 步驟單一對照表**：合併 **現行 8 步**、**BU 實務 10 步**，並借鑑 **Graphify** 的 detect／triage／多模態分流概念。  
**執行時** Agent 仍依 [**PROMPTS.md**](./PROMPTS.md) § Ingest 全文操作；規約見 [**AGENTS.md**](../AGENTS.md)。

> **主幹**：一鍵多模態進得來 → 轉成可追溯 Markdown 歸檔 → 產出 OKF `wiki/`。**不**以 `graph.json` 為知識本體；Graphify 僅作未來可選外掛（階段 2）。

---

## 三步驟對照總表

| 合併步驟 | 現行 8 步 | BU 10 步 | Graphify 概念 |
|----------|-----------|----------|----------------|
| **1** 讀取指定來源 | ① 讀取指定來源 | ① 讀取指定來源／批次 | 指定 `INPUT_PATH` |
| **2** Detect／Triage | — | ② Triage 檔型與視覺 | `detect`：分類 code／docs／papers／images |
| **3** 多模態轉 Markdown | — | ③ 轉換＋視覺閘 | 依副檔名 extractor |
| **4** 原件歸檔 `raw/originals/` | — | （④ 歸檔流程內） | — |
| **5** 視覺資產 `raw/assets/` | — | ③ 視覺閘產物 | 圖片抽出 |
| **6** 歸檔 `raw/sources/<slug>.md` | ② 歸檔 sources | ④ Archive converted MD | — |
| **7** 建立／更新 `wiki/sources/` | ③ wiki sources | ⑤ Create/update sources | — |
| **8** 抽取 concepts／entities | ④ 抽取 | ⑥ Extract | — |
| **9** 更新相關頁與連結 | ⑤⑥ 更新＋連結 | ⑦⑧ Link | — |
| **10** OKF frontmatter | （併入 PROMPTS 5） | — | — |
| **11** 更新 `wiki/index.md` | ⑦ 更新 index | ⑨ Update index | `--wiki` 僅參考，非本管線產物 |
| **12** append `wiki/log.md` | ⑧ Append log | ⑩ Append log | — |

---

## 合併後 12 步（階段 1 標準）

### A. 輸入與分流（借鑑 Graphify + BU）

**1. 讀取指定來源**  
路徑可為：使用者訊息中的檔案、URL 下載檔、`raw/inbox/` 內待處理檔，或明確的 ingest 批次目錄。未提供時向使用者索取。

**2. Detect／Triage**  
對每個檔案判斷：

| 檢查項 | 動作 |
|--------|------|
| 副檔名 | 見下方「支援輸入類型」 |
| 是否含資訊性視覺 | 流程圖、架構圖、截圖、掃描頁、ER、簡報圖 |
| 可否直達 Ingest | `.md` 且內容已結構化 → 可跳過轉檔 |

**3. 多模態轉 Markdown**（非 `.md` 或 `.md` 內嵌不可讀視覺時）  
依類型轉為 **結構化繁體中文 Markdown**（技術詞保留英文）。含資訊性視覺時 **必須** 依 [**visual-source-conversion.md**](./visual-source-conversion.md) 處理（含 **硬閘**：文字層極短但有架構圖時，須 vision 對圖寫層／節點盤點，嚴禁只寫標題）。使用者無須另下「請轉視覺」指令。

### B. 不可變歸檔（BU + OKF）

**4. 原件歸檔**（若輸入非純文字 Markdown）  
將 PDF、DOCX、PPTX 等 **原始檔** 複製至 `raw/originals/`（新檔；勿改寫既有檔）。檔名建議保留原識別名或加日期前綴。

**5. 視覺資產**（若步驟 3 有萃取）  
圖片、截圖、簡報頁匯出等寫入 `raw/assets/`，並在 Markdown 中以相對路徑引用。

**6. 歸檔 canonical Markdown**  
**新增** `raw/sources/<slug>.md`（僅新檔；遵循 **檔案與路徑命名**）。  
- **粒度**：**盡可能詳盡還原**（非 wiki 級精簡）；逐頁／逐段、圖內標籤與表格須寫入正文（見 **visual-source-conversion.md** → **`raw/sources/` 與 `wiki/sources/` 分工**）。  
- **slug**：繁體字面或英文識別名（見 **docs/okf.md** → resource 語意）。  
- **修訂**：來源改版時 **另建新檔**（可選 `YYYYMMDD_<slug>.md` 或新 slug），勿就地改寫舊歸檔。  
- 在歸檔稿文末或 log 簡述：triage 結果、是否執行視覺轉換、轉換限制。

### C. OKF Knowledge Bundle（現行主幹）

**7. 建立／更新 `wiki/sources/<slug>.md`**  
**摘要頁**（從步驟 6 歸檔稿抽取，非全文複製）；區塊標題須符合 **來源頁 Schema**；版型：**page-template-source.md**。  
`resource` 指向歸檔 slug（修訂稿則指向新 slug）。

**8. 抽取 `wiki/concepts/*`、`wiki/entities/*`**  
依歸檔與來源頁內容；版型：**page-template-concept.md**。

**9. 更新相關頁並建立連結**  
**markdown 相對路徑**；盡量雙向。冷啟動時新頁至少連結一個其他 wiki 頁（常為 `../index.md`）。

**10. 補齊 OKF 建議 frontmatter**  
`description`、`resource`（slug 或 URL）、`timestamp`（ISO 8601）；見 **docs/okf.md**。

**11. 更新 `wiki/index.md`**  
於 **Sources**、**Concepts**、**Entities** 等區加 **連結 + 一行說明**。

**12. append `wiki/log.md`**  
格式：`## [YYYY-MM-DD] ingest | <title>`；含 triage／轉檔摘要（或註明「無需視覺轉換」）。

---

## 支援輸入類型（階段 1）

| 類型 | 副檔名 | 處理 |
|------|--------|------|
| Markdown | `.md` | 可直接歸檔；內嵌視覺仍走視覺閘 |
| 純文字 | `.txt` | 轉 Markdown 標題結構 |
| Word | `.docx` | 轉 Markdown（標題、表格、列表） |
| PDF | `.pdf` | 轉 Markdown（保留頁碼／章節；圖表走視覺閘） |
| 簡報 | `.ppt` `.pptx` | 每張投影片一節（投影片編號、標題、表格、圖） |
| 試算表 | `.xlsx` | 每工作表一節或表格 |
| 圖片 | `.png` `.jpg` `.webp` | 視覺閘 → 文字描述 + `raw/assets/` |

HTML、程式碼庫批次等：階段 1 可逐檔處理或列為 **Limitations**；階段 2 再評估外掛工具。

---

## `raw/` 目錄角色

```text
raw/
  inbox/       # 使用者丟入待處理原件（可含 PDF、Office、圖片）
  originals/   # 處理後保留之非 Markdown 原件（不可變）
  sources/     # canonical Markdown 歸檔（Ingest 主要依據）
  assets/      # 自視覺萃取之圖片／附件
```

`wiki/` 為 **OKF bundle**；`raw/` 為可追溯擴充，不在 OKF bundle 本體內。

---

## 與 Graphify 的邊界（階段 1）

| 項目 | 本管線 | Graphify（階段 2 可選） |
|------|--------|-------------------------|
| 知識本體 | `wiki/**/*.md` | `graphify-out/graph.json` |
| 多模態 | Agent 依本檔 + visual doc 轉檔 | CLI 自動 extract |
| 關係 | `## Relationships` + 相對連結 | 圖遍歷、社群 |
| 查詢 | `/query` 讀 wiki | `graphify query` |

---

## 相關文件

- [AGENTS.md](../AGENTS.md) — 操作：Ingest、來源轉換政策
- [PROMPTS.md](./PROMPTS.md) — Ingest 提示詞（複製貼上）
- [onboarding.md](./onboarding.md) — 第一輪上手
- [visual-source-conversion.md](./visual-source-conversion.md) — 視覺內容轉換
- [okf.md](./okf.md) — `resource` slug、連結、匯出
