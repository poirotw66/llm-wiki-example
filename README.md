# llm-wiki-example（OKF Knowledge Bundle 範本）

供各部門 **fork／GitHub Template** 後自建 wiki 的 **起步 repo**：`wiki/` 為 **[OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) Knowledge Bundle**（**內容留白**，以 Ingest 填入）、`raw/` 歸檔擴充與 [SKILL.md](SKILL.md)。規約見 [**AGENTS.md**](AGENTS.md)；OKF 對照見 [**docs/okf.md**](docs/okf.md)；Agent 提示詞見 [**docs/PROMPTS.md**](docs/PROMPTS.md)。

---

## 採用指南（給各部門）

本 repo 是 **範本**，不是各部門共用的知識庫。

### 三步開始

1. **建立部門專用 repo** — 使用 **Use this template** 或 fork 後改名；**勿**在本 example 倉寫部門內容。  
2. **客製化** — 編輯 [`wiki/index.md`](wiki/index.md) 的 **Overview**（部門名稱、範圍）；必要時微調 [**AGENTS.md**](AGENTS.md)。  
3. **第一次 Ingest** — 參考 [docs/onboarding.md](docs/onboarding.md) 與 [docs/templates/](docs/templates/)；在 Cursor 輸入 **`/ingest <路徑>`**（詳見下方 **Cursor Skill 用法**）。  
   - **Skill**：fork 後可直接用內建 [`.cursor/skills/`](.cursor/skills/)；若要裝到 Claude Code／Codex 或本機全域，見下方 **[npx skills 安裝](#npx-skills-安裝可選)**。

### 日常在做什麼

| 操作 | 何時用 |
|------|--------|
| **Ingest** | 新文件／規格要納入 wiki |
| **Query** | 向 wiki 提問（可重用答案寫入 `wiki/queries/`） |
| **Lint** | 定期或 PR 前檢查品質 |
| **FAQ** / **Graph** | 主題夠多或關係複雜時（進階） |

步驟、格式、硬約束 → [**AGENTS.md**](AGENTS.md)。

---

## Cursor Skill 用法

本 repo 內建 **薄 Skill**（[`.cursor/skills/`](.cursor/skills/) 與 [`skills/`](skills/) 同步），fork 後可直接在 **Cursor Agent** 使用。在對話框輸入觸發詞即可；Agent 會讀 [AGENTS.md](AGENTS.md) 並依 [docs/PROMPTS.md](docs/PROMPTS.md) 對應章節執行（步驟只維護在 PROMPTS，Skill 不重複全文）。

### npx skills 安裝（可選）

使用 [vercel-labs/skills](https://www.npmjs.com/package/skills) CLI，從 GitHub repo 安裝 Skill 到 Cursor、Claude Code、Codex 等 Agent。Skill 原始檔在 [`skills/`](skills/)（與 [`.cursor/skills/`](.cursor/skills/) 同步）；`npx skills add` 會掃描 `skills/<name>/SKILL.md`，共 **6 個**（總覽 `llm-wiki-example` + 五個操作）。

#### 何時需要

| 情境 | 建議 |
|------|------|
| 已 fork，用 Cursor 開 wiki repo | **不必**跑 npx；內建 `.cursor/skills/` 即可 |
| 要裝到 **Claude Code** 或 **Codex** | 用下方 `npx skills add` |
| 希望 **本機所有專案** 都能觸發 `/ingest` 等 | 加 `-g` 全域安裝 |
| 在本 repo **開發／驗證** Skill | `npx skills add . ...` |

#### 前置條件

- 已安裝 **Node.js**（可執行 `npx`）
- 遠端安裝：GitHub 上已有可存取的 repo（fork 後請將 `<owner>` 換成你的 `org/repo`，例如 `your-org/llm-wiki`）
- 範本來源：`poirotw66/llm-wiki-example`（未 fork 可直接引用；部門 wiki 建議改用自己的 repo）

#### 安裝指令

```bash
# Cursor + Claude Code + Codex（僅本專案／目前工作目錄）
npx skills add <owner>/llm-wiki-example -a cursor -a claude-code -a codex -y

# 全域（本機所有專案）
npx skills add <owner>/llm-wiki-example -a cursor -a claude-code -a codex -g -y

# 本 repo 全部 Skill → 所有偵測到的 Agent
npx skills add <owner>/llm-wiki-example --all -y

# 本地開發（於 repo 根目錄；不需 push GitHub）
npx skills add . --all -a cursor -y

# 只安裝單一 Skill（例：Ingest）
npx skills add <owner>/llm-wiki-example --skill llm-wiki-ingest -a cursor -y

# 安裝前先列出可發現的 Skill
npx skills add <owner>/llm-wiki-example --list
```

**範例**（使用本範本 repo）：

```bash
npx skills add poirotw66/llm-wiki-example -a cursor -a claude-code -a codex -y
```

#### 安裝後

- **Cursor（專案）**：Skill 通常寫入 `.agents/skills/`（與內建 `.cursor/skills/` 並存；擇一維護即可，建議以 `skills/` 為單一來源）
- **Cursor（全域 `-g`）**：`~/.cursor/skills/`
- Skill 執行時以 **工作區根目錄** 的 `AGENTS.md`、`docs/PROMPTS.md` 為準 — 請以 **wiki repo 為工作區根** 開啟，勿嵌在子目錄而無對應規約檔

### 觸發一覽

| 輸入 | 用途 | Skill |
|------|------|-------|
| `/ingest <路徑或 URL>` | 歸檔來源、更新 wiki | [llm-wiki-ingest](skills/llm-wiki-ingest/SKILL.md) |
| `/query <問題>` | 向 wiki 提問（可寫入 `wiki/queries/`） | [llm-wiki-query](skills/llm-wiki-query/SKILL.md) |
| `/lint` | 品質檢查、斷鏈、產出 `wiki/lint/` | [llm-wiki-lint](skills/llm-wiki-lint/SKILL.md) |
| `/faq` | 自現有 wiki 產生 FAQ 題組 | [llm-wiki-faq](skills/llm-wiki-faq/SKILL.md) |
| `/graph` | 知識關係圖摘要 | [llm-wiki-graph](skills/llm-wiki-graph/SKILL.md) |

不確定用哪個操作時，可參考總覽 [skills/llm-wiki-example/SKILL.md](skills/llm-wiki-example/SKILL.md)。

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
4. 部門 wiki：**append** [wiki/log.md](wiki/log.md)

### 不用 Skill 時

亦可直接複製 [docs/PROMPTS.md](docs/PROMPTS.md) 對應章節貼給任意 LLM Agent。

---

## 專案目的

建立 **符合 OKF、以來源為根據、可追溯、可連結演進** 的 Markdown 知識包，供 LLM／人類維護，並支援 FAQ、onboarding、RAG、Agent 與他方 OKF 工具互通。

---

## 文件地圖

| 檔案 | 用途 |
|------|------|
| [**AGENTS.md**](AGENTS.md) | OKF 主軸、目錄契約、頁面格式、五大操作 |
| [**docs/okf.md**](docs/okf.md) | OKF v0.1 對照、合規、匯出／匯入 |
| [**docs/PROMPTS.md**](docs/PROMPTS.md) | Agent 複製貼上提示詞（**步驟單一來源**） |
| [**SKILL.md**](SKILL.md) | npx skills 安裝說明（`metadata.internal`） |
| [**skills/llm-wiki-example/**](skills/llm-wiki-example/SKILL.md) | 總覽 Skill（npx 可發現） |
| [**skills/llm-wiki-*/**](skills/) | 五個薄 Skill + 總覽（`npx skills add` 來源） |
| [`.cursor/skills/llm-wiki-*/`](.cursor/skills/) | 與 `skills/` 同步（fork 內建 Cursor 路徑） |
| [**docs/onboarding.md**](docs/onboarding.md) | 第一輪 Ingest 解說 |
| [**wiki/README.md**](wiki/README.md) | OKF bundle（`wiki/`）目錄樹與連結 |
| [**docs/templates/page-template-source.md**](docs/templates/page-template-source.md) | `wiki/sources/*` 版型 |
| [**docs/templates/page-template-concept.md**](docs/templates/page-template-concept.md) | `wiki/concepts/*`、`entities/*`、`queries/*` 版型 |

---

## 快速連結

- **給 Agent 複製貼上** → [docs/PROMPTS.md](docs/PROMPTS.md)
- **Skill** → [skills/llm-wiki-example/](skills/llm-wiki-example/SKILL.md) · `/ingest` … `/graph` → [skills/](skills/) 或 [.cursor/skills/](.cursor/skills/) · **npx 安裝** → 見上方 [npx skills 安裝](#npx-skills-安裝可選)
- **wiki 總目錄** → [wiki/index.md](wiki/index.md)
- **部門上手** → [docs/onboarding.md](docs/onboarding.md)
