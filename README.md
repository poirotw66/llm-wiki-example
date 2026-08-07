# llm-wiki-example（OKF Knowledge Bundle 範本）

供各部門 **fork／GitHub Template** 後自建 wiki 的 **起步 repo**。`wiki/` 為 **[OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) Knowledge Bundle**（**內容刻意留白**，以 `/ingest` 填入）；`raw/` 為不可變歸檔擴充；薄 Skill 見 [`skills/`](skills/)（**Git 追蹤的單一來源**；`.cursor/` 已 gitignore）。

寫入或分享內容前，須依 [**docs/data-governance.md**](docs/data-governance.md) 完成分類、PII、遮罩、owner 與 Git 准入確認。

| 需求 | 檔案／指令 |
|------|------------|
| 規約與五大操作 | [**AGENTS.md**](AGENTS.md) |
| OKF 對照 | [**docs/okf.md**](docs/okf.md) |
| 資料分類、PII 與 Git 准入 | [**docs/data-governance.md**](docs/data-governance.md) |
| Agent 提示詞（步驟單一來源） | [**docs/PROMPTS.md**](docs/PROMPTS.md) |
| Ingest 步驟（含快取／兩段式／Review） | [**docs/ingest-pipeline.md**](docs/ingest-pipeline.md)／[PROMPTS](docs/PROMPTS.md) |
| 第一輪 Ingest | [**docs/onboarding.md**](docs/onboarding.md) |
| PDF 轉譯 SOP | [**docs/pdf-ingest-sop.md**](docs/pdf-ingest-sop.md) |
| 視覺閘／Visual Evidence | [**docs/visual-source-conversion.md**](docs/visual-source-conversion.md)（就地放置；**讀圖一律 subagent**） |
| PDF 初始化安裝 | 見下方 **初始化安裝**（預設只需 **Poppler**；Docling 可選）；詳見 [docs/pdf-ingest-sop.md](docs/pdf-ingest-sop.md) |
| Wiki lint | `uv run --group test python3 scripts/wiki-lint.py` |
| Ingest 清理 | `python3 scripts/ingest-cleanup.py <input> --archive raw/originals/<original> --archive raw/sources/<slug>.md`（先 dry-run，確認後加 `--confirm`） |
| Wiki 重置為空白 | `uv run python scripts/wiki-reset.py`（dry-run）→ `--confirm`（保留 `wiki/lint/`；append log） |
| PDF helper | `uv run python scripts/docling-pdf.py ...`（**預設 fast**；**僅使用者指定**才 `--engine docling`／full） |
| Ingest SHA 快取 | `python3 scripts/ingest-cache.py lookup\|record …` |
| Review 佇列 | `python3 scripts/ingest-review.py append\|close …` → `ops/review-queue.md` |
| Graph 洞見 | `python3 scripts/wiki-graph-insights.py` → `ops/graph-insights.md` |
| Skill token 報表 | `python3 scripts/wiki-usage.py report --by skill`（[docs/skill-usage.md](docs/skill-usage.md)） |
| 頁面版型 | [**docs/templates/**](docs/templates/) |
| CI（schema／raw 不可變／log） | [`.github/workflows/wiki-quality.yml`](.github/workflows/wiki-quality.yml) |
| npx skills 安裝 | [**SKILL.md**](SKILL.md) |

---

## 目錄結構

```text
raw/                    # 不可變歸檔（非 OKF bundle 本體）
  inbox/                # 待處理原件（MD、PDF、Office、圖片…）
  originals/            # 所有輸入原件位元副本（含 Markdown）
  sources/              # canonical Markdown 歸檔稿
  assets/               # 視覺萃取附件（raw/assets/<base-slug>/p<NN>.png）
wiki/                   # OKF Knowledge Bundle（fork 後以 Ingest 填入）
  index.md              # 總目錄（okf_version: "0.2" + catalog）
  log.md                # 操作日誌（append only）
  sources/ concepts/ entities/ queries/ faq/ lint/ graph/
docs/                   # 支援文件（非 wiki 知識本體）
  PROMPTS.md  ingest-pipeline.md  pdf-ingest-sop.md
  visual-source-conversion.md  onboarding.md  okf.md
  data-governance.md  skill-usage.md  templates/
scripts/                # wiki-lint、ingest-cleanup、ingest-cache、ingest-review、
                        # wiki-graph-insights、wiki-reset、docling-pdf、wiki-usage
.github/workflows/      # wiki-quality CI
models/docling/         # 可選 Docling 模型（本機下載；已 gitignore；約 1.2GB）
config/                 # skill-usage 費率等設定
.llm-wiki/usage/        # append-only Skill 使用量 ledger（events.jsonl）
.llm-wiki/ingest/       # SHA 快取＋兩段式分析稿（本機；已 gitignore）
ops/                    # bundle 外操作狀態：purpose、review queue、graph insights
skills/                 # 薄 Skill 單一來源（npx / 本機同步）
AGENTS.md  SKILL.md  README.md
pyproject.toml  uv.lock  .python-version
```

`.cursor/`（含本機 `skills` 副本）與 `models/docling/` **不進 Git**；見 [`.gitignore`](.gitignore)。

### `raw/originals/` vs `raw/sources/`

寫入 `raw/` 前仍須通過 [企業資料治理與 Git 准入](docs/data-governance.md)：`confidential`／`restricted`、PII 或未知 PII 預設不得將原件、OCR、截圖或可還原內容提交到 Git。`raw/` 的不可變性不是准入授權。

| 目錄 | 角色 |
|------|------|
| **`raw/originals/`** | 每次 Ingest **一律**放入輸入原件（**含 `.md`**、PDF、Office、圖片）；不可變位元副本 |
| **`raw/sources/`** | 自 originals **轉寫／清理／補強**後的 canonical Markdown 歸檔稿（wiki 摘要的依據） |
| **`wiki/sources/`** | OKF 來源**摘要頁**（非歸檔全文） |

成功歸檔後會刪除 `raw/inbox/` 或 repo 根目錄的輸入副本（原件已在 `raw/originals/`）。

**輸入偏好**：優先提供**可選取文字**的 PDF／Markdown／Office；純圖或掃描簡報會觸發大量 vision，成本與空殼風險較高（仍可 ingest，見 [visual-source-conversion.md](docs/visual-source-conversion.md) 驗收／自動重派）。

### Ingest 檔案流程

一次 `/ingest` 時，檔案大致這樣走（細節見 [docs/ingest-pipeline.md](docs/ingest-pipeline.md)）：

```text
輸入（路徑／raw/inbox／批次）
        │
        ▼
 資料治理閘（classification／PII／遮罩；見 data-governance）
        │
        ▼
 Detect／Triage（檔型、是否轉檔、是否含資訊圖）
        │
        ├─ PDF：pdftotext 初稿＋頁級分流（預設 fast；可只跑部分頁）
        ├─ 資訊圖頁：匯出 raw/assets/ → **subagent 讀圖**寫 Visual Evidence
        │
        ▼
 raw/originals/     ← 一律位元複製原件（含 .md）
        │
        ├─（若有）raw/assets/<base-slug>/p<NN>.png
        │
        ▼
 raw/sources/<archive-slug>.md   ← 詳盡歸檔（VE **就地**插入；修訂另建新檔）
        │
        ▼
 wiki/sources/ 摘要頁 ＋ 抽取 concepts／entities
        │
        ▼
 更新 wiki/index.md、雙向連結、append wiki/log.md
        │
        ▼
 刪除 inbox／根目錄輸入副本（禁止刪 raw/ 歸檔本體）
```

| 階段 | 產物 | 說明 |
|------|------|------|
| 輸入 | 使用者路徑或 `raw/inbox/*` | MD／PDF／Office／圖片等 |
| 原件 | `raw/originals/<原檔名>` | **不可變**；MD 也要複製，不可省略 |
| 視覺 | `raw/assets/<base-slug>/p<NN>.png` | 僅資訊性視覺；目錄用 `<base-slug>`（部分頁亦同） |
| 歸檔稿 | `raw/sources/<archive-slug>.md` | 詳盡還原；部分頁 slug 例：`<base-slug>-頁1至5` |
| Wiki | `wiki/sources`、`concepts`、`entities` | 摘要與知識頁；OKF v0.2 frontmatter＋治理欄位；更新 `index.md` |
| 收尾 | 刪輸入副本；append `log.md` | 原件已在 `originals/` |

**觸發範例**

```text
/ingest raw/inbox/某規格.pdf
/ingest raw/inbox/                 # 批次處理 inbox 內待處理檔
/ingest ./內部說明.md              # 根目錄 MD：先入 originals，再寫 sources
/ingest ./手冊.pdf 前五頁          # 部分頁 → archive-slug `…-頁1至5`
```

部分頁的產物命名、CLI 與 checklist 見 [docs/pdf-ingest-sop.md → 部分頁 Ingest](docs/pdf-ingest-sop.md#部分頁-ingest第一次用)、[docs/onboarding.md](docs/onboarding.md#部分頁-ingest第一次用建議)。文字層空時以 vision 為準（不硬優化 OCR）。

**硬約束（摘要）**

- 勿改寫既有 `raw/` 檔；修訂請另建新歸檔
- 架構圖／流程圖禁止只抄標題；Visual Evidence **就地**放置，禁止文末彙整
- **讀圖一律 subagent**（主 Agent 禁止自行 `Read` 圖片）；多張平行派工
- Concept 須合 OKF v0.2（`type`、`generated`、lifecycle）與本倉治理欄位（見 [docs/okf.md](docs/okf.md)、[docs/data-governance.md](docs/data-governance.md)）
- 寫入前通過資料治理 Git 准入

細節：[docs/visual-source-conversion.md](docs/visual-source-conversion.md)、[docs/pdf-ingest-sop.md](docs/pdf-ingest-sop.md)。

### 初始化安裝（建議；含 PDF Ingest）

核心 wiki 腳本（lint、cleanup、usage）**不必**裝 PDF 組。若會 `/ingest` PDF，**預設 fast 路徑只需 Poppler**（不必下載 ~1.2GB Docling 模型）。細節見 [**docs/pdf-ingest-sop.md**](docs/pdf-ingest-sop.md)。

**PDF 引擎政策**：**一律預設 `fast`**（`pdftotext` + 頁級視覺閘）。**僅當使用者明確指定**（例如「用 full」「用 Docling」「`--engine docling`」）才改走 Docling；Agent **不得**自行因「複雜表格／有 GPU」升級。

```bash
# 0) 安裝 uv（若尚未安裝）
#    https://docs.astral.sh/uv/getting-started/installation/

# 1) 系統工具：pdfinfo／pdftotext／pdftoppm（Poppler）— 預設 fast 必備
#    macOS:   brew install poppler
#    Ubuntu:  sudo apt install poppler-utils
#    Windows: winget install --id oschwartz10612.Poppler -e
#             （安裝後重新開一個終端機，讓 PATH 生效）

# 2) 確認 helper（預設 --engine fast，不載入 Docling）
uv run python scripts/docling-pdf.py --help
pdfinfo -v

# --- 可選：僅在使用者指定 full／Docling 時 ---
# uv sync --group pdf
# uv run docling-tools models download -o models/docling
```

| 項目 | 說明 |
|------|------|
| 預設引擎 | **`fast`**（`pdftotext` + `pdftoppm`）；**不需** Docling 模型 |
| full／Docling | **僅使用者指定**時用 `--engine docling`；需先裝模型（`models/docling/`） |
| 覆寫 | `DOCLING_ARTIFACTS_PATH`（僅 docling 引擎） |
| CLI | 用 `uv run python ...`（Windows 上 `python3` 常不可用） |
| Python | **3.12** 建議（`.python-version`）；`>=3.10,<3.14` |
| 部分頁 | `uv run python scripts/docling-pdf.py <pdf> --page-from 1 --page-to 5 --export-vision-assets` |
| 輸入偏好 | **可選文字** PDF／MD／Office 優先；純圖簡報會全頁 vision |
| 回到空白 | `uv run python scripts/wiki-reset.py` → 確認後 `--confirm`（見 [onboarding](docs/onboarding.md#回到範本空白可選)） |

---

## 採用指南（給各部門）

本 repo 是 **範本**，不是各部門共用的知識庫。`wiki/` 預設空白。

### 三步開始

1. **建立部門專用 repo** — **Use this template** 或 fork 後改名；**勿**在本 example 倉寫部門內容。
2. **客製化** — 編輯 [`ops/purpose.md`](ops/purpose.md)（正式採用時改為 `mode: production` 並完成目標／問題）與 [`wiki/index.md`](wiki/index.md) Overview；設定資料 owner／分類規則（[data-governance.md](docs/data-governance.md)）；必要時微調 [**AGENTS.md**](AGENTS.md)。
3. **安裝 Skill 並第一次 Ingest** — 見下方 **npx skills 安裝** 與 [docs/onboarding.md](docs/onboarding.md)。若會 ingest PDF，先完成上方 **初始化安裝（建議；含 PDF Ingest）**。再在 Cursor 輸入 **`/ingest <路徑>`**（預設 fast；兩段式分析；同檔 SHA 命中會 skip）。

### 日常操作

| 操作 | 何時用 | 空白 wiki 時 |
|------|--------|----------------|
| **Ingest** | 新文件納入 wiki（**MD／PDF／Office／圖片**） | ✅ 第一步 |
| **Query** | 向 wiki 提問 | 可答「尚無內容」；可寫入 `wiki/queries/` |
| **Lint** | 定期或 PR 前品質檢查 | ✅ 可跑（多為 pass） |
| **FAQ** | 主題夠多、要題組頁 | ⚠️ 須先有內容；否則 **no-op** |
| **Graph** | 關係複雜、要知識圖 | ⚠️ 須先有內容；否則 **no-op** |

步驟與硬約束 → [**AGENTS.md**](AGENTS.md) · 空 wiki 行為 → [**docs/PROMPTS.md**](docs/PROMPTS.md)。

---

## Cursor Skill 用法

薄 Skill 定義在 [`skills/`](skills/)。在 **Cursor Agent** 輸入觸發詞；Agent 讀 [AGENTS.md](AGENTS.md) 並依 [docs/PROMPTS.md](docs/PROMPTS.md) 對應章節執行（**步驟只維護在 PROMPTS**）。

**維護 Skill 時**：只改 [`skills/`](skills/)（總覽 + 五個操作）。本機可同步到 `.cursor/skills/`（已 gitignore）。

### npx skills 安裝（建議）

使用 [vercel-labs/skills](https://www.npmjs.com/package/skills) CLI，從 repo 的 `skills/` 安裝。`npx skills add` 掃描共 **6 個** Skill（總覽 + 五個操作）。

| 情境 | 建議 |
|------|------|
| 已 fork，用 Cursor 開 wiki repo | **建議**跑 `npx skills add` |
| 要裝到 Claude Code／Codex | 用下方指令加對應 `-a` |
| 本機所有專案都能觸發 | 加 `-g` |
| 在本 repo 開發／驗證 Skill | `npx skills add . ...` |

```bash
# Cursor + Claude Code + Codex（僅本專案）
npx skills add <owner>/llm-wiki-example -a cursor -a claude-code -a codex -y

# 全域
npx skills add <owner>/llm-wiki-example -a cursor -a claude-code -a codex -g -y

# 本地開發（於 repo 根目錄）
npx skills add . --all -a cursor -y

# 範例（本範本遠端）
npx skills add poirotw66/llm-wiki-example -a cursor -a claude-code -a codex -y
```

安裝後請以 **wiki repo 為工作區根** 開啟（Skill 依根目錄 `AGENTS.md`、`docs/PROMPTS.md` 執行）。

### 觸發一覽

| 輸入 | 用途 | Skill |
|------|------|-------|
| `/ingest <路徑或 URL>` | 歸檔來源、更新 wiki | [llm-wiki-ingest](skills/llm-wiki-ingest/SKILL.md) |
| `/query <問題>` | 向 wiki 提問 | [llm-wiki-query](skills/llm-wiki-query/SKILL.md) |
| `/lint` | 品質檢查、斷鏈 | [llm-wiki-lint](skills/llm-wiki-lint/SKILL.md) |
| `/faq` | 產生 FAQ 題組 | [llm-wiki-faq](skills/llm-wiki-faq/SKILL.md) |
| `/graph` | 知識關係圖 | [llm-wiki-graph](skills/llm-wiki-graph/SKILL.md) |

### 範例指令

```text
/ingest ./規格.md
/ingest raw/inbox/
/ingest raw/inbox/某規格.pdf
/ingest ./手冊.pdf 前五頁
/query <你的問題>
/lint
/faq
/graph
```

### 執行後 Agent 應完成

1. 依 **AGENTS.md** 硬約束（引用、連結、OKF v0.2 frontmatter、治理欄位、`raw/` 不可變、讀圖 subagent 等）
2. 依 **PROMPTS.md** 該操作步驟全文執行（Ingest：originals → sources → wiki）
3. 必要時更新 [wiki/index.md](wiki/index.md)
4. 開始執行 `python3 scripts/wiki-usage.py start <operation> --title "<title>"`，append [wiki/log.md](wiki/log.md) 後執行 `python3 scripts/wiki-usage.py finish <operation> --title "<title>"`（無變更時記 pass／no-op）

### 不用 Skill 時

直接複製 [docs/PROMPTS.md](docs/PROMPTS.md) 對應章節貼給任意 LLM Agent。

---

## 專案目的

建立 **符合 OKF v0.2、以來源為根據、可追溯、可連結演進** 的 Markdown 知識包，供 LLM／人類維護，並支援 FAQ、onboarding、RAG、Agent 與他方 OKF 工具互通；同時以本倉治理欄位與 CI lint 強化企業准入。

---

## 文件地圖

| 檔案 | 用途 |
|------|------|
| [**AGENTS.md**](AGENTS.md) | OKF 主軸、目錄契約、頁面格式、五大操作 |
| [**docs/okf.md**](docs/okf.md) | OKF v0.2 對照、合規、遷移、匯出／匯入 |
| [**docs/data-governance.md**](docs/data-governance.md) | 分類、owner、PII、保存、遮罩、人工核可與 Git 准入 |
| [**docs/PROMPTS.md**](docs/PROMPTS.md) | Agent 提示詞（**步驟單一來源**） |
| [**docs/ingest-pipeline.md**](docs/ingest-pipeline.md) | Ingest 管線對照（完整步驟以 PROMPTS／AGENTS 為準） |
| [**docs/pdf-ingest-sop.md**](docs/pdf-ingest-sop.md) | PDF 轉譯 SOP（預設 fast；full／Docling 僅使用者指定） |
| [**docs/visual-source-conversion.md**](docs/visual-source-conversion.md) | Visual Evidence 就地放置、讀圖一律 subagent、強制提示詞 |
| [**docs/onboarding.md**](docs/onboarding.md) | 第一輪 Ingest |
| [**docs/skill-usage.md**](docs/skill-usage.md) | Skill token／usage ledger |
| [**docs/templates/**](docs/templates/) | 來源頁／概念頁版型 |
| [**wiki/index.md**](wiki/index.md) | OKF bundle 總目錄（預設空白；`okf_version: "0.2"`） |
| [**docs/wiki-bundle.md**](docs/wiki-bundle.md) | `wiki/` bundle 導覽 |
| [**SKILL.md**](SKILL.md) | npx skills 安裝 |
| [**skills/**](skills/) | 薄 Skill（**唯一 Git 來源**） |
| [**pyproject.toml**](pyproject.toml)／[**uv.lock**](uv.lock) | uv 依賴；可選 PDF／Docling 組見 `uv sync --group pdf` |
| [**config/**](config/) | usage 費率等設定 |
| [**scripts/**](scripts/) | lint、cleanup、wiki-reset、docling-pdf、wiki-usage |
| [**.github/workflows/wiki-quality.yml**](.github/workflows/wiki-quality.yml) | PR／push：pytest + wiki-lint |

---

## 快速連結

- **給 Agent 複製貼上** → [docs/PROMPTS.md](docs/PROMPTS.md)
- **Skill** → [skills/llm-wiki-example/](skills/llm-wiki-example/SKILL.md) · **npx** → [SKILL.md](SKILL.md)
- **wiki 總目錄** → [wiki/index.md](wiki/index.md)
- **部門上手** → [docs/onboarding.md](docs/onboarding.md)
- **資料治理** → [docs/data-governance.md](docs/data-governance.md)
