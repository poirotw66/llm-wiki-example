# llm-wiki-example（LLM Wiki 範例工作區）

本倉庫是以 [**AGENTS.md**](AGENTS.md) 為單一規約來源的 **空白 LLM Wiki 起步結構**：目錄、`wiki/index.md`、`wiki/log.md`、版型與操作提示皆已就位，可直接 `git clone` 使用，無須另建 scaffold。

---

## 專案目的

本專案示範如何維護一個 **持久、可追溯、偏圖結構（graph-aware）、以來源為根據（source-grounded）** 的知識庫，讓 LLM 或人類維護者能長期演進內容，並服務於 FAQ、onboarding、RAG、Agent 等情境。

具體目標包括：

- **降低幻覺**：主張有來源才寫入，主張可驗證。
- **提高可追溯性**：主張引用路徑、區塊與日誌紀錄。
- **維持關係結構**：概念、實體、來源之間以連結與可選的 Relationships 區塊表達，利於之後做圖推理或檢索。
- **提高重用性**：透過 `queries`、`faq` 等區塊累積可重複使用的問答與流程知識。

設計上遵循 **AGENTS.md** 中的行為原則：保守優於發揮、明確優於暗示、連結優於孤立、結構優於冗長；並對應「以來源為根據優於臆測、結構優於篇幅、連結優於單頁、演進優於一次完美」等核心取向。

---

## 與 AGENTS.md 的關係

[**AGENTS.md**](AGENTS.md) 是本 wiki 的 **維護契約**：規定目錄意義、頁面格式、連結與引用規則、各種「操作」（Ingest／Query／FAQ／Lint／Graph）的步驟，以及何時必須更新 [`wiki/index.md`](wiki/index.md)、append [`wiki/log.md`](wiki/log.md)。本 README 為 **入門與導覽**；執行細節與給 Agent 的複製貼上英文提示，以 [**docs/OPERATIONS.md**](docs/OPERATIONS.md) 為準（與 **AGENTS.md** 一致）。

以下依 **AGENTS.md** 架構說明各區功能（精簡版；完整條文請直接閱讀該檔）。

### 目錄契約（資料放哪裡）

| 路徑 | 功能說明 |
|------|----------|
| [`raw/`](raw/) | **既有來源的不可變區**：不可就地改寫既有檔。**Ingest** 時可將**新**來源歸檔至 `raw/sources/*.md`。 |
| [`wiki/`](wiki/) | **由 LLM／維護者管理的知識庫本體**（Markdown）。 |
| [`wiki/index.md`](wiki/index.md) | **總目錄**（單一檔）：固定章節順序（Overview → Concepts → Entities → Sources → Queries → FAQ）。條目格式為 **連結 + 一行說明**。 |
| [`wiki/log.md`](wiki/log.md) | **僅可 append 的操作日誌**：每次完成 **AGENTS.md** 定義之操作皆應留下紀錄（含 pass／no-op）。 |
| [`wiki/sources/`](wiki/sources/) | 自歸檔來源整理而來的 **來源頁**（需符合 Source Page Schema）。 |
| [`wiki/concepts/`](wiki/concepts/) | **抽象概念**（例如 API、Transaction）。 |
| [`wiki/entities/`](wiki/entities/) | **具體系統／技術實體**（例如某框架、某資料庫驅動）。 |
| [`wiki/queries/`](wiki/queries/) | **可重用的問答型知識**。 |
| [`wiki/faq/`](wiki/faq/) | **結構化 FAQ 頁**（題組、範圍、相關頁連結）。 |
| [`wiki/lint/`](wiki/lint/) | **檢查／診斷結果**（矛盾、過時、孤兒頁等）。 |
| [`wiki/graph/`](wiki/graph/) | **關係對照／圖摘要**（選用、進階）。 |
| [`docs/`](docs/) | **支援用文件**，不計入 wiki 知識本體；含版型索引與 **OPERATIONS.md**。 |

### 頁面與索引約定

- **格式**：僅 Markdown；除 `wiki/index.md` 外，wiki 頁需含 **YAML frontmatter**（`title`、`type`、`status`、`updated`、`source_count`、`tags` 等，詳見 **AGENTS.md**）。
- **語言**：內文以 **繁體中文** 為主；技術名詞可用英文（API、MVC 等）。
- **粒度**：一頁一概念或一實體；過長宜拆；避免混用不同抽象層次。
- **目錄結構**：預設不把 Overview 拆成獨立 `wiki/overview.md`；**Overview 與各分類目錄** 皆在 **`wiki/index.md`** 內依規定標題排列。

### 連結、知識圖、引用與不確定性

- **連結（強制）**：每頁至少連到另一頁；新頁必須被別處引用；盡量雙向連結。
- **知識關係**：允許 concept／entity／source 之間的語意關係；可選 `## Relationships` 區塊以利之後 RAG／Agent 推理。
- **引用（強制）**：可驗證敘述須標註來源，例如 `[[sources/ch1]]`。
- **不確定性**：使用（確定）、（推測）、（未知）等標記，避免偽裝成有來源的斷言。

### 來源頁（`wiki/sources/*`）專用區塊

每則來源頁須包含 **Summary、Key Concepts、Entities、Notable Claims、Limitations / Gaps** 等標題（與 **AGENTS.md** 及 [`docs/templates/page-template-source.md`](docs/templates/page-template-source.md) 對齊）。其他類型頁面可使用 [`docs/templates/page-template-concept.md`](docs/templates/page-template-concept.md)；版型索引見 [`docs/templates/page-template.md`](docs/templates/page-template.md)。

### 五大操作（Agent／人類維護流程）

| 操作 | 目的與要點（對應 **AGENTS.md**） |
|------|----------------------------------|
| **Ingest** | 讀指定來源 → **新檔**歸檔至 `raw/sources/*.md` → 建立或更新 `wiki/sources/*` → 抽取 concepts／entities → 更新相關頁與連結 → 更新 **`wiki/index.md`** → **append `wiki/log.md`**。 |
| **Query** | 讀索引 → 找相關頁 → 綜合回答 → **引用來源** → 標不確定性 → 若可重用則持久化 → 更新索引與日誌。**解析順序**：先 faq／concepts／entities 摘要；不足或衝突時回到 `raw/sources/*`；答案須含可追溯路徑（必要時到章節／行）。 |
| **FAQ** | 從現有 wiki 掃描主題與重複模式 → 產出 8–15 題（含初階與跨頁綜合題，不可虛構題目）→ 寫入 `wiki/faq/*` → 更新 **`wiki/index.md`** FAQ 區 → **append `wiki/log.md`**。 |
| **Lint** | 偵測矛盾、過時、孤兒頁、缺頁、重複概念、無來源頁、超過 30 天未更新等 → 輸出至 `wiki/lint/`；若新增或實質變更 lint 產物且目錄需露出，則更新 **`wiki/index.md`**；**每次執行皆 append `wiki/log.md`**（含通過／簡短摘要）。 |
| **Graph** | 遍歷頁面、抽取連結、推論關係、產出圖摘要（例如 `wiki/graph/knowledge-map.md`）；若圖產物新增或實質變更則更新索引；**每次執行皆 append `wiki/log.md`**（含 no-op）。 |

### 硬約束（維護時必守）

- **不可**在未獲明確核准下，就地修改 `raw/` 既有檔；Ingest 僅透過 **新增** `raw/sources/` 歸檔。
- 不可無標記地臆測；宣稱須能引用；頁面須有連結網路。
- 完成 **AGENTS.md** 所定義之任一操作時，**一律** append **`wiki/log.md`**；若該次操作會新增／刪除／實質變更 wiki 頁或目錄所列產物，則須更新 **`wiki/index.md`**（各操作另有更細的索引更新規則，以 **AGENTS.md** 為準）。

---

## 快速開始

1. **取得本倉**：`git clone` 或將本 repo 設為 GitHub Template 後建立新倉，即可獲得完整目錄與規約。
2. **第一次寫入知識**：依 **AGENTS.md** 執行 **Ingest**（流程摘要見上表）；逐步補上 `wiki/sources`、`concepts`、`entities` 並更新 **`wiki/index.md`** 與 **`wiki/log.md`**。
3. **給 Agent 的逐步指令**：使用 [**docs/OPERATIONS.md**](docs/OPERATIONS.md) 內的英文複製提示與編號檢查清單。
4. **資料夾導覽**：見 [**wiki/README.md**](wiki/README.md)。

---

## Graphify 與 `graphify-out/`

本範例 **不納入** graphify 類工具之產物目錄（例如 `graphify-out/GRAPH_REPORT.md`）。若你本機安裝 graphify 並執行分析，產物會落在 `graphify-out/`（已列於 [.gitignore](.gitignore)，不會誤提交）。部分 Cursor 工作區規則若提及讀取 `graphify-out/`，在本倉可能 **不存在該路徑**，屬預期；可改以 **`wiki/index.md`**、**AGENTS.md** 與原始碼為架構參考，或於本機產生 graphify 報告後再讀。
