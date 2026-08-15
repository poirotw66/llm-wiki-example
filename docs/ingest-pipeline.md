# Ingest 管線（階段 1：多模態合併版）

本檔為 **Ingest 步驟對照表**。執行時以 [**PROMPTS.md**](./PROMPTS.md) § Ingest 與 [**AGENTS.md**](../AGENTS.md) → **操作：Ingest** 為準（編號 **0–16**）。

> **主幹**：治理閘 →（可選）SHA 快取 skip → 多模態轉檔／視覺閘 → 不可變歸檔 → **兩段式分析** → 保證 wiki 來源摘要 → concepts／entities → Review 佇列 → 清理 → log／cache record。  
> **不**以 `graph.json` 為知識本體；Graphify 僅作歷史借鑑／階段 2 可選外掛。

---

## 步驟對照總表（0–16）

| 步驟 | 內容 | 產物／腳本 | 舊 8 步 | BU 10 步 | Graphify 概念 |
|------|------|------------|---------|----------|----------------|
| **0** | 資料治理閘 | 分類／PII／owner／准入；必要時停自動寫入 | — | — | — |
| **1** | 讀取指定來源 | 路徑／`raw/inbox/`／批次 | ① | ① | `INPUT_PATH` |
| **2** | SHA-256 快取 lookup | `uv run python scripts/ingest-cache.py lookup`；hit → no-op | — | — | — |
| **3** | Detect／Triage | 檔型、轉檔需求、資訊性視覺 | — | ② | `detect` |
| **4** | 多模態轉 Markdown | PDF：**fast**；`vision_pages` 非空 → 強制 Vision subagent | — | ③ | extractor |
| **5** | 原件歸檔 | `raw/originals/`（一律，含 MD） | — | （④ 內） | — |
| **6** | 視覺資產 | `raw/assets/<base-slug>/p<NN>.png` | — | ③ 產物 | 圖片抽出 |
| **7** | canonical 歸檔 | `raw/sources/<archive-slug>.md` | ② | ④ | — |
| **8** | 兩段式 · 分析 | `.llm-wiki/ingest/analyses/<archive-slug>.md` | — | — | — |
| **9** | 保證來源摘要頁 | `wiki/sources/<archive-slug>.md`（lint 硬閘） | ③ | ⑤ | — |
| **10** | 抽取 concepts／entities | `wiki/concepts/*`、`wiki/entities/*` | ④ | ⑥ | — |
| **11** | 更新頁面與雙向連結 | 相對路徑 `.md` | ⑤⑥ | ⑦⑧ | — |
| **12** | OKF + 治理 frontmatter | `archive_slug`、`sources[]`、`generated`… | （併入） | — | — |
| **13** | 更新 index／purpose | `wiki/index.md`；可選 `ops/purpose.md` thesis | ⑦ | ⑨ | — |
| **14** | 非同步 Review | `uv run python scripts/ingest-review.py append` → `ops/review-queue.md` | — | — | — |
| **15** | append log + cache record | `wiki/log.md`；`uv run python scripts/ingest-cache.py record --sha256 …` | ⑧ | ⑩ | — |
| **16** | 輸入原件清理 | `scripts/ingest-cleanup.py`（dry-run → `--confirm`） | — | — | — |

**外層 wrapper（不計入 0–16）**：`uv run python scripts/wiki-usage.py start ingest --title "…"`／`finish ingest --title "…"`。

開始前讀 [**ops/purpose.md**](../ops/purpose.md)。

---

## 詳細步驟

### A. 閘與輸入（0–4）

**0. 資料治理閘**  
依 [data-governance.md](./data-governance.md) 判定分類、PII、owner、scope、retention、redaction 與 Git 准入。未通過時不寫入 `raw/`、不送外部工具，改走人工核可／例外流程。

**1. 讀取指定來源**  
路徑可為：使用者訊息中的檔案、URL 下載檔、`raw/inbox/` 內待處理檔，或明確的 ingest 批次目錄。未提供時向使用者索取。

**2. SHA-256 快取**  
```bash
uv run python scripts/ingest-cache.py lookup "<path>"
```
- `hit: true` 且使用者未要求強制重跑 → append `wiki/log.md` **no-op**（註明 sha256／既有 archive_slug）並 `finish ingest`。
- 強制重跑：使用者明示，或 lookup 加 `--force`。

**3. Detect／Triage**  

| 檢查項 | 動作 |
|--------|------|
| 副檔名 | 見下方「支援輸入類型」 |
| 是否含資訊性視覺 | 流程圖、架構圖、截圖、掃描頁、ER、簡報圖；PDF 以 helper 的 `vision_pages` 為準 |
| 可否直達歸檔整理 | `.md` 且內容已結構化 → 可跳過轉檔，仍須 originals＋canonical sources |

視覺閘分支（固定；Agent **自動**執行，勿等使用者再指定）：

```text
detect/triage
  → vision_pages 非空？（或其他資訊圖硬閘）
    → 是：render（pdftoppm／--export-vision-assets）
         → Vision subagent（每頁／每圖；層／節點／箭頭盤點）
         → 就地 Visual Evidence
         → 繼續文字轉換／歸檔
    → 否：繼續文字轉換（log／歸檔註明「視覺轉換閘：未適用」）
```

**4. 多模態轉 Markdown**（非 `.md` 或 `.md` 內嵌不可讀視覺時）  
依類型轉為 **結構化繁體中文 Markdown**（技術詞保留英文）。**PDF** 依 [**pdf-ingest-sop.md**](./pdf-ingest-sop.md)：`scripts/docling-pdf.py`（預設 `--engine fast`）→ 文字／表格直入；`vision_pages` 非空時 **必須** `pdftoppm` + Vision subagent（見上方分支）。**僅使用者指定**時才 `--engine docling`。含資訊性視覺時 **必須** 依 [**visual-source-conversion.md**](./visual-source-conversion.md)（硬閘、就地放置、**讀圖一律 subagent**）。**禁止**在 `vision_pages` 未跑完 Vision 前建立 wiki 頁。

### B. 不可變歸檔（5–7）

**5. 原件歸檔**（**一律**，含 Markdown）  
將輸入原件 **位元複製**至 `raw/originals/`（新檔；勿改寫既有檔）。**不可**因輸入已是 Markdown 而跳過。

**6. 視覺資產**（若步驟 4 有萃取）  
寫入 `raw/assets/<base-slug>/`（PDF 檔名 **`p<NN>.png`**，見 **pdf-ingest-sop.md**），並在 Markdown 以相對路徑引用。

**7. 歸檔 canonical Markdown**  
**新增** `raw/sources/<archive-slug>.md`（僅新檔）。  
- **來源**：自 `raw/originals/` 轉寫、清理或補強（PDF 等經 `pdftotext`／可選 Docling／vision）。  
- **粒度**：**盡可能詳盡還原**；Visual Evidence **就地**放置。  
- **slug**：全檔／部分頁／修訂規則見 **pdf-ingest-sop.md**、**okf.md**。  
- **修訂**：另建新檔，勿改寫舊歸檔。

### C. 兩段式分析與 wiki 寫入（8–13）

**8. 兩段式 · 分析（強制）**  
依 [**templates/ingest-analysis.md**](./templates/ingest-analysis.md) 寫入 `.llm-wiki/ingest/analyses/<archive-slug>.md`：  
實體／概念／與既有 wiki 連結／矛盾與張力／建議落點／review candidates。將分析檔 SHA-256、canonical `raw/sources` SHA-256、actor、時間與版本寫入來源頁 `analysis_receipt`，僅保存 receipt、不保存私有分析正文。
**禁止**未寫分析就產生 wiki 頁。

**9. 保證來源摘要頁**  
建立或更新 `wiki/sources/<archive-slug>.md`（來源頁 Schema；有圖必含 **`## Visual Assets`**）。  
lint：每個 `raw/sources/*.md` 必須有對應 `wiki/sources/<同名>.md`。

**10. 抽取 concepts／entities**  
依分析稿與歸檔；版型 **page-template-concept.md**。

**11. 更新相關頁並雙向連結**  
markdown 相對路徑；冷啟動時新頁至少連一個其他 wiki 頁（常為 `../index.md`）。

**12. 補齊 OKF v0.2 + 治理 frontmatter**  
`description`、`sources`、`generated`、`status`，必要時 `verified`／`stale_after`、來源頁 `archive_slug` 與六個治理欄位。不可把 agent 自評寫成 `human:` 驗證。

**13. 更新 `wiki/index.md`**  
於 **Sources**、**Concepts**、**Entities** 等區加 **連結 + 一行說明**。有根據時可微調 `ops/purpose.md` → Evolving thesis。

### D. Review、清理與留痕（14–16）

**14. 非同步 Review**  
對分析中的 review candidates、未答 Q&A、需人審治理項：  
```bash
uv run python scripts/ingest-review.py append --title "…" --reason "…" --action human_verify|create_page|deep_research|governance|skip
```  
寫入 `ops/review-queue.md`；**不**阻擋本輪 wiki 寫入。

**15. append log + cache record**
在 destructive cleanup 前，使用步驟 2 lookup 的 SHA-256 記錄成功 ingest：
```bash
uv run python scripts/ingest-cache.py record --sha256 "<lookup-sha256>" --original-name "<原檔名>" --archive-slug "<slug>" --source-page "wiki/sources/<slug>.md" --analysis-receipt "<analysis-sha256>" --analysis-source-sha256 "<archive-sha256>" --analysis-generated-by "<actor>" --analysis-generated-at "<ISO-8601>"
```

**16. 輸入原件清理**
步驟 5（originals）與步驟 7（sources）成功後，僅可清理 `raw/inbox/` 或 repo 根目錄的明確支援輸入檔。  
```bash
uv run python scripts/ingest-cleanup.py "<input>" --archive "raw/originals/…" --archive "raw/sources/<slug>.md"
# 確認後再加 --confirm
```
**禁止**刪 `raw/` 歸檔本體、目錄、symlink。

- Append `wiki/log.md`（triage／轉檔／vision／cache／cleanup 摘要）。

---

## 支援輸入類型（階段 1）

| 類型 | 副檔名 | 處理 |
|------|--------|------|
| Markdown | `.md` | **先**入 `raw/originals/`；再寫 canonical 至 `raw/sources/`；內嵌視覺仍走視覺閘 |
| 純文字 | `.txt` | 轉 Markdown 標題結構 |
| Word | `.docx` | 轉 Markdown（標題、表格、列表） |
| PDF | `.pdf` | 依 [**pdf-ingest-sop.md**](./pdf-ingest-sop.md)：預設 fast；**僅使用者指定**才 Docling；支援全檔或頁面範圍 |
| 簡報 | `.ppt` `.pptx` | 每張投影片一節 |
| 試算表 | `.xlsx` | 每工作表一節或表格 |
| 圖片 | `.png` `.jpg` `.webp` | 視覺閘 → 文字描述 + `raw/assets/` |

HTML、程式碼庫批次等：階段 1 可逐檔處理或列為 **Limitations**。

---

## `raw/` 與工作目錄

```text
raw/
  inbox/       # 待處理原件
  originals/   # 輸入原件副本（不可變）
  sources/     # canonical Markdown 歸檔稿
  assets/      # 視覺萃取附件
.llm-wiki/ingest/          # 本機工作產物（gitignore）
  cache.json               # SHA-256 → 已 ingest 對照
  analyses/<archive-slug>.md
wiki/
  sources/ concepts/ entities/
  index.md  log.md
ops/
  purpose.md               # 方向（bundle 外操作資料）
  review-queue.md          # 非同步人審
```

`wiki/` 為 **OKF bundle**；`raw/` 與 `.llm-wiki/ingest/` 為本倉擴充。

---

## 與 Graphify 的邊界（階段 1）

| 項目 | 本管線 | Graphify（階段 2 可選） |
|------|--------|-------------------------|
| 知識本體 | `wiki/**/*.md` | `graphify-out/graph.json` |
| 多模態 | Agent 依本檔 + visual／pdf SOP | CLI 自動 extract |
| 關係 | `## Relationships` + 相對連結；`/graph` + insights | 圖遍歷、社群 |
| 查詢 | `/query`（可 Read Sources Only） | `graphify query` |

---

## 相關文件

- [AGENTS.md](../AGENTS.md) — 操作：Ingest、來源轉換政策
- [PROMPTS.md](./PROMPTS.md) — Ingest 提示詞（步驟單一來源）
- [templates/ingest-analysis.md](./templates/ingest-analysis.md) — 兩段式分析骨架
- [onboarding.md](./onboarding.md) — 第一輪上手
- [visual-source-conversion.md](./visual-source-conversion.md) — 視覺轉換
- [pdf-ingest-sop.md](./pdf-ingest-sop.md) — PDF SOP
- [data-governance.md](./data-governance.md) — 治理閘
- [okf.md](./okf.md) — `archive_slug`、resource、連結與匯出
