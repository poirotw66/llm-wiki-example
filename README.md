# llm-wiki-example（OKF Knowledge Bundle 範本）

供各部門 **fork／GitHub Template** 後自建 wiki 的 **起步 repo**。`wiki/` 為 **[OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) Knowledge Bundle**（**內容留白**，以 Ingest 填入）；`raw/` 為不可變歸檔擴充；薄 Skill 見 [`skills/`](skills/)（與 [`.cursor/skills/`](.cursor/skills/) 同步）。

| 需求 | 檔案 |
|------|------|
| 規約與五大操作 | [**AGENTS.md**](AGENTS.md) |
| OKF 對照 | [**docs/okf.md**](docs/okf.md) |
| Agent 提示詞（步驟單一來源） | [**docs/PROMPTS.md**](docs/PROMPTS.md) |
| 第一輪 Ingest | [**docs/onboarding.md**](docs/onboarding.md) |
| 頁面版型 | [**docs/templates/**](docs/templates/) |
| npx skills 安裝 | [**SKILL.md**](SKILL.md) |

---

## 目錄結構

```text
raw/                    # 不可變歸檔（非 OKF bundle 本體）
  sources/              # 文字來源歸檔（Ingest 寫入）
  assets/               # 圖片／附件（選用）
wiki/                   # OKF Knowledge Bundle（fork 後以 Ingest 填入）
  index.md              # 總目錄（okf_version + catalog）
  log.md                # 操作日誌（append only）
  sources/ concepts/ entities/ queries/ faq/ lint/ graph/
docs/                   # 支援文件（非 wiki 知識本體）
  onboarding.md  okf.md  PROMPTS.md  templates/
skills/                 # npx skills 標準格式（維護單一來源）
.cursor/skills/         # 與 skills/ 同步（Cursor fork 內建）
AGENTS.md  SKILL.md  README.md
```

---

## 採用指南（給各部門）

本 repo 是 **範本**，不是各部門共用的知識庫。

### 三步開始

1. **建立部門專用 repo** — 使用 **Use this template** 或 fork 後改名；**勿**在本 example 倉寫部門內容。
2. **客製化** — 編輯 [`wiki/index.md`](wiki/index.md) 的 **Overview**（部門名稱、範圍）；必要時微調 [**AGENTS.md**](AGENTS.md)。
3. **第一次 Ingest** — 參考 [docs/onboarding.md](docs/onboarding.md) 與 [docs/templates/](docs/templates/)；在 Cursor 輸入 **`/ingest <路徑>`**（詳見下方 **Cursor Skill 用法**）。
   - **Skill**：fork 後可直接用內建 [`.cursor/skills/`](.cursor/skills/)；若要裝到 Claude Code／Codex 或本機全域，見 **[npx skills 安裝](#npx-skills-安裝可選)**。

### 日常在做什麼

| 操作 | 何時用 | 空白 wiki 時 |
|------|--------|----------------|
| **Ingest** | 新文件／規格要納入 wiki | ✅ 第一步 |
| **Query** | 向 wiki 提問 | 可答「尚無內容」；可寫入 `wiki/queries/` |
| **Lint** | 定期或 PR 前檢查品質 | ✅ 可跑（多為 pass） |
| **FAQ** | 主題夠多、要題組頁 | ⚠️ 須先有內容；否則 **no-op** |
| **Graph** | 關係複雜、要知識圖 | ⚠️ 須先有內容；否則 **no-op** |

步驟、格式、硬約束 → [**AGENTS.md**](AGENTS.md) · 空 wiki 行為 → [**docs/PROMPTS.md**](docs/PROMPTS.md)（FAQ／Graph 章節）。

---

## Cursor Skill 用法

本 repo 內建 **薄 Skill**（[`.cursor/skills/`](.cursor/skills/) 與 [`skills/`](skills/) 同步）。在 **Cursor Agent** 輸入觸發詞；Agent 讀 [AGENTS.md](AGENTS.md) 並依 [docs/PROMPTS.md](docs/PROMPTS.md) 對應章節執行（**步驟只維護在 PROMPTS**，Skill 不重複全文）。

**維護 Skill 時**：以 [`skills/`](skills/) 為單一來源，修改後同步至 [`.cursor/skills/`](.cursor/skills/)（五個操作 Skill；總覽僅在 `skills/llm-wiki-example/`）。

### npx skills 安裝（可選）

使用 [vercel-labs/skills](https://www.npmjs.com/package/skills) CLI，從 GitHub repo 安裝到 Cursor、Claude Code、Codex 等。`npx skills add` 掃描 `skills/<name>/SKILL.md`，共 **6 個**（總覽 + 五個操作）。

#### 何時需要

| 情境 | 建議 |
|------|------|
| 已 fork，用 Cursor 開 wiki repo | **不必**跑 npx；內建 `.cursor/skills/` 即可 |
| 要裝到 **Claude Code** 或 **Codex** | 用下方 `npx skills add` |
| 希望 **本機所有專案** 都能觸發 `/ingest` 等 | 加 `-g` 全域安裝 |
| 在本 repo **開發／驗證** Skill | `npx skills add . ...` |

#### 前置條件

- 已安裝 **Node.js**（可執行 `npx`）
- 遠端安裝：GitHub 上已有可存取的 repo（fork 後將 `<owner>` 換成你的 `org/repo`）
- 範本來源：`poirotw66/llm-wiki-example`（部門 wiki 建議改用自己的 repo）

#### 安裝指令

```bash
# Cursor + Claude Code + Codex（僅本專案）
npx skills add <owner>/llm-wiki-example -a cursor -a claude-code -a codex -y

# 全域（本機所有專案）
npx skills add <owner>/llm-wiki-example -a cursor -a claude-code -a codex -g -y

# 全部 Skill → 全部偵測到的 Agent
npx skills add <owner>/llm-wiki-example --all -y

# 本地開發（於 repo 根目錄）
npx skills add . --all -a cursor -y

# 只安裝單一 Skill
npx skills add <owner>/llm-wiki-example --skill llm-wiki-ingest -a cursor -y

# 安裝前列出
npx skills add <owner>/llm-wiki-example --list
```

**範例**：

```bash
npx skills add poirotw66/llm-wiki-example -a cursor -a claude-code -a codex -y
```

#### 安裝後

- **Cursor（專案）**：通常寫入 `.agents/skills/`（與 `.cursor/skills/` 並存）
- **Cursor（全域 `-g`）**：`~/.cursor/skills/`
- 請以 **wiki repo 為工作區根** 開啟（Skill 依根目錄 `AGENTS.md`、`docs/PROMPTS.md` 執行）

### 觸發一覽

| 輸入 | 用途 | Skill |
|------|------|-------|
| `/ingest <路徑或 URL>` | 歸檔來源、更新 wiki | [llm-wiki-ingest](skills/llm-wiki-ingest/SKILL.md) |
| `/query <問題>` | 向 wiki 提問 | [llm-wiki-query](skills/llm-wiki-query/SKILL.md) |
| `/lint` | 品質檢查、斷鏈 | [llm-wiki-lint](skills/llm-wiki-lint/SKILL.md) |
| `/faq` | 產生 FAQ 題組 | [llm-wiki-faq](skills/llm-wiki-faq/SKILL.md) |
| `/graph` | 知識關係圖 | [llm-wiki-graph](skills/llm-wiki-graph/SKILL.md) |

總覽：[skills/llm-wiki-example/SKILL.md](skills/llm-wiki-example/SKILL.md)

### 範例指令

```text
/ingest ./docs/內部規格.md
/query <你的問題>
/lint
/faq
/graph
```

### 執行後 Agent 應完成

1. 依 **AGENTS.md** 硬約束（引用、連結、frontmatter 等）
2. 依 **PROMPTS.md** 該操作步驟全文執行
3. 必要時更新 [wiki/index.md](wiki/index.md)
4. **append** [wiki/log.md](wiki/log.md)（無變更時記 pass／no-op）

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
| [**docs/okf.md**](docs/okf.md) | OKF v0.1 對照、合規、匯出／匯入 |
| [**docs/PROMPTS.md**](docs/PROMPTS.md) | Agent 提示詞（**步驟單一來源**） |
| [**docs/onboarding.md**](docs/onboarding.md) | 第一輪 Ingest 解說 |
| [**docs/templates/page-template-source.md**](docs/templates/page-template-source.md) | `wiki/sources/*` 版型 |
| [**docs/templates/page-template-concept.md**](docs/templates/page-template-concept.md) | `wiki/concepts/*`、`entities/*`、`queries/*` 版型 |
| [**wiki/index.md**](wiki/index.md) | OKF bundle 總目錄 |
| [**wiki/README.md**](wiki/README.md) | `wiki/` 目錄樹與連結 |
| [**SKILL.md**](SKILL.md) | npx skills 安裝說明 |
| [**skills/**](skills/) | 薄 Skill（npx 來源） |
| [**.cursor/skills/**](.cursor/skills/) | 與 `skills/` 同步（Cursor 內建） |

---

## 快速連結

- **給 Agent 複製貼上** → [docs/PROMPTS.md](docs/PROMPTS.md)
- **Skill** → [skills/llm-wiki-example/](skills/llm-wiki-example/SKILL.md) · **npx** → [SKILL.md](SKILL.md)
- **wiki 總目錄** → [wiki/index.md](wiki/index.md)
- **部門上手** → [docs/onboarding.md](docs/onboarding.md)
