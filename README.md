# llm-wiki-example（OKF Knowledge Bundle 範本）

供各部門 **fork／GitHub Template** 後自建 wiki 的 **起步 repo**。`wiki/` 為 **[OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) Knowledge Bundle**（**內容刻意留白**，以 `/ingest` 填入）；`raw/` 為不可變歸檔擴充；薄 Skill 見 [`skills/`](skills/)（**Git 追蹤的單一來源**；`.cursor/` 已 gitignore）。

| 需求 | 檔案／指令 |
|------|------------|
| 規約與五大操作 | [**AGENTS.md**](AGENTS.md) |
| OKF 對照 | [**docs/okf.md**](docs/okf.md) |
| 資料分類、PII 與 Git 准入 | [**docs/data-governance.md**](docs/data-governance.md) |
| Agent 提示詞（步驟單一來源） | [**docs/PROMPTS.md**](docs/PROMPTS.md) |
| Ingest 13 步管線 | [**docs/ingest-pipeline.md**](docs/ingest-pipeline.md) |
| 第一輪 Ingest | [**docs/onboarding.md**](docs/onboarding.md) |
| PDF 轉譯 SOP | [**docs/pdf-ingest-sop.md**](docs/pdf-ingest-sop.md) |
| PDF 依賴（uv） | `uv sync --group pdf` 後 `uv run docling-tools models download -o models/docling`（詳見 [docs/pdf-ingest-sop.md](docs/pdf-ingest-sop.md)） |
| Wiki lint | `python3 scripts/wiki-lint.py` |
| Ingest 清理 | `python3 scripts/ingest-cleanup.py <input> --archive raw/originals/<original> --archive raw/sources/<slug>.md`（先 dry-run，確認後加 `--confirm`） |
| PDF Docling helper | `uv run python scripts/docling-pdf.py ...` |
| Skill token 報表 | `python3 scripts/wiki-usage.py report --by skill`（[docs/skill-usage.md](docs/skill-usage.md)） |
| 頁面版型 | [**docs/templates/**](docs/templates/) |
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
  index.md              # 總目錄（okf_version + catalog）
  log.md                # 操作日誌（append only）
  sources/ concepts/ entities/ queries/ faq/ lint/ graph/
docs/                   # 支援文件（非 wiki 知識本體）
  PROMPTS.md  ingest-pipeline.md  pdf-ingest-sop.md
  visual-source-conversion.md  onboarding.md  okf.md
  skill-usage.md  templates/
scripts/                # wiki-lint、ingest-cleanup、docling-pdf、wiki-usage
models/docling/         # Docling 預設模型（本機下載；已 gitignore；約 1.2GB）
config/                 # skill-usage 費率等設定
.llm-wiki/usage/        # append-only Skill 使用量 ledger（events.jsonl）
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

### Ingest 檔案流程

一次 `/ingest` 時，檔案大致這樣走（細節見 [docs/ingest-pipeline.md](docs/ingest-pipeline.md)）：

```text
輸入（路徑／raw/inbox／批次）
        │
        ▼
 Detect／Triage（檔型、是否轉檔、是否含資訊圖）
        │
        ├─ 需要時：轉 Markdown（PDF→Docling；資訊圖→vision）
        │
        ▼
 raw/originals/     ← 一律位元複製原件（含 .md）
        │
        ├─（若有）raw/assets/<base-slug>/p<NN>.png
        │
        ▼
 raw/sources/<slug>.md   ← canonical 詳盡歸檔稿（新檔；修訂另建）
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
| 視覺 | `raw/assets/<base-slug>/p<NN>.png` | 僅資訊性視覺需要 |
| 歸檔稿 | `raw/sources/<slug>.md` | 詳盡還原，非 wiki 精簡版 |
| Wiki | `wiki/sources`、`concepts`、`entities` | 摘要與知識頁；更新 `index.md` |
| 收尾 | 刪輸入副本；append `log.md` | 原件已在 `originals/` |

**觸發範例**

```text
/ingest raw/inbox/某規格.pdf
/ingest raw/inbox/                 # 批次處理 inbox 內待處理檔
/ingest ./內部說明.md              # 根目錄 MD：先入 originals，再寫 sources
```

**硬約束（摘要）**：勿改寫既有 `raw/` 檔；修訂請另建新歸檔；有架構圖／流程圖時禁止只抄標題（見 [docs/visual-source-conversion.md](docs/visual-source-conversion.md)、[docs/pdf-ingest-sop.md](docs/pdf-ingest-sop.md)）。

### Python 依賴與 Docling 模型（uv）

可選 PDF 路徑（Docling／torch）以 [uv](https://docs.astral.sh/uv/) 管理。核心 wiki 腳本（lint、cleanup、usage）**不必**安裝 PDF 組。完整前置（poppler、平台 torch 表、常見錯誤）見 [**docs/pdf-ingest-sop.md**](docs/pdf-ingest-sop.md) → **前置（安裝）**。

```bash
# 安裝 uv：https://docs.astral.sh/uv/getting-started/installation/
uv sync --group pdf
# 預設模型組（勿只傳 rapidocr）→ models/docling/（gitignore；約 1.2GB）
uv run docling-tools models download -o models/docling
uv run python scripts/docling-pdf.py --help
```

| 項目 | 說明 |
|------|------|
| 模型目錄 | `models/docling/`（`scripts/docling-pdf.py` 預設） |
| 覆寫 | `DOCLING_ARTIFACTS_PATH` |
| CLI | 用 `uv run docling-tools ...`（勿直接打 `docling-tools`） |
| Python | **3.12** 建議（`.python-version`）；`>=3.10,<3.14`；Intel Mac torch 鎖定見 `pyproject.toml` |

---

## 採用指南（給各部門）

本 repo 是 **範本**，不是各部門共用的知識庫。`wiki/` 預設空白。

### 三步開始

1. **建立部門專用 repo** — **Use this template** 或 fork 後改名；**勿**在本 example 倉寫部門內容。
2. **客製化** — 編輯 [`wiki/index.md`](wiki/index.md) 的 **Overview**（部門名稱、範圍）；必要時微調 [**AGENTS.md**](AGENTS.md)。
3. **安裝 Skill 並第一次 Ingest** — 見下方 **npx skills 安裝** 與 [docs/onboarding.md](docs/onboarding.md)；在 Cursor 輸入 **`/ingest <路徑>`**（或把檔案放入 `raw/inbox/` 後 `/ingest raw/inbox`）。

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
/query <你的問題>
/lint
/faq
/graph
```

### 執行後 Agent 應完成

1. 依 **AGENTS.md** 硬約束（引用、連結、frontmatter、`raw/` 不可變等）
2. 依 **PROMPTS.md** 該操作步驟全文執行（Ingest：originals → sources → wiki）
3. 必要時更新 [wiki/index.md](wiki/index.md)
4. 開始／結束執行 `python3 scripts/wiki-usage.py start|finish <operation>`，並 **append** [wiki/log.md](wiki/log.md)（無變更時記 pass／no-op）

### 不用 Skill 時

直接複製 [docs/PROMPTS.md](docs/PROMPTS.md) 對應章節貼給任意 LLM Agent。

---

## 專案目的

建立 **符合 OKF、以來源為根據、可追溯、可連結演進** 的 Markdown 知識包，供 LLM／人類維護，並支援 FAQ、onboarding、RAG、Agent 與他方 OKF 工具互通。

---

## 文件地圖

| 檔案 | 用途 |
|------|------|
| [**AGENTS.md**](AGENTS.md) | OKF 主軸、目錄契約、頁面格式、五大操作 |
| [**docs/okf.md**](docs/okf.md) | OKF v0.2 對照、合規、遷移、匯出／匯入 |
| [**docs/data-governance.md**](docs/data-governance.md) | 分類、owner、PII、保存、遮罩、人工核可與 Git 准入 |
| [**docs/PROMPTS.md**](docs/PROMPTS.md) | Agent 提示詞（**步驟單一來源**） |
| [**docs/ingest-pipeline.md**](docs/ingest-pipeline.md) | Ingest 13 步（多模態） |
| [**docs/pdf-ingest-sop.md**](docs/pdf-ingest-sop.md) | PDF 轉譯 SOP（安裝前置、`models/docling/`、Docling + 視覺閘） |
| [**docs/visual-source-conversion.md**](docs/visual-source-conversion.md) | 視覺來源轉換 |
| [**docs/onboarding.md**](docs/onboarding.md) | 第一輪 Ingest |
| [**docs/skill-usage.md**](docs/skill-usage.md) | Skill token／usage ledger |
| [**docs/templates/**](docs/templates/) | 來源頁／概念頁版型 |
| [**wiki/index.md**](wiki/index.md) | OKF bundle 總目錄（預設空白） |
| [**wiki/README.md**](wiki/README.md) | `wiki/` 目錄導覽 |
| [**SKILL.md**](SKILL.md) | npx skills 安裝 |
| [**skills/**](skills/) | 薄 Skill（**唯一 Git 來源**） |
| [**pyproject.toml**](pyproject.toml)／[**uv.lock**](uv.lock) | uv 依賴；PDF 組見 `uv sync --group pdf` + 模型下載 |
| [**config/**](config/) | usage 費率等設定 |
| [**scripts/**](scripts/) | lint、cleanup、docling-pdf、wiki-usage |

---

## 快速連結

- **給 Agent 複製貼上** → [docs/PROMPTS.md](docs/PROMPTS.md)
- **Skill** → [skills/llm-wiki-example/](skills/llm-wiki-example/SKILL.md) · **npx** → [SKILL.md](SKILL.md)
- **wiki 總目錄** → [wiki/index.md](wiki/index.md)
- **部門上手** → [docs/onboarding.md](docs/onboarding.md)
