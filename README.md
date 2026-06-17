# llm-wiki-example（OKF Knowledge Bundle 範本）

供各部門 **fork／GitHub Template** 後自建 wiki 的 **起步 repo**：`wiki/` 為 **[OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) Knowledge Bundle**，含虛構示範頁、`raw/` 歸檔擴充與 [SKILL.md](SKILL.md)。規約見 [**AGENTS.md**](AGENTS.md)；OKF 對照見 [**docs/okf.md**](docs/okf.md)；Agent 提示詞見 [**docs/PROMPTS.md**](docs/PROMPTS.md)。

---

## 採用指南（給各部門）

本 repo 是 **範本**，不是各部門共用的知識庫。

### 三步開始

1. **建立部門專用 repo** — 使用 **Use this template** 或 fork 後改名；**勿**在本 example 倉寫部門內容。  
2. **客製化** — 編輯 [`wiki/index.md`](wiki/index.md) 的 **Overview**；刪除或覆寫標有 `範例` 的示範頁（含 `queries/`、`faq/`）與 `raw/sources/訂單-api-簡介.md`；必要時微調 [**AGENTS.md**](AGENTS.md)。  
3. **第一次 Ingest** — 參考本倉 [`wiki/`](wiki/) 示範與 [**docs/onboarding.md**](docs/onboarding.md)；在 Cursor 可輸入 **`/ingest <路徑>`**（見 [`.cursor/skills/`](.cursor/skills/)）或複製 [**docs/PROMPTS.md**](docs/PROMPTS.md) 請 Agent 執行。

### 日常在做什麼

| 操作 | 何時用 |
|------|--------|
| **Ingest** | 新文件／規格要納入 wiki |
| **Query** | 向 wiki 提問（可重用答案寫入 `wiki/queries/`） |
| **Lint** | 定期或 PR 前檢查品質 |
| **FAQ** / **Graph** | 主題夠多或關係複雜時（進階） |

步驟、格式、硬約束 → [**AGENTS.md**](AGENTS.md)。Cursor 薄 Skill：`/ingest`、`/query`、`/lint`、`/faq`、`/graph` → [`.cursor/skills/`](.cursor/skills/)（步驟委派 **PROMPTS**，勿在 Skill 內複製）。

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
| [**SKILL.md**](SKILL.md) | 總覽 Skill；子 Skill 見 [`.cursor/skills/`](.cursor/skills/) |
| [`.cursor/skills/llm-wiki-*/`](.cursor/skills/) | 五個薄 Skill（`/ingest` … `/graph`） |
| [**docs/onboarding.md**](docs/onboarding.md) | 第一輪 Ingest 解說 |
| [**wiki/README.md**](wiki/README.md) | OKF bundle（`wiki/`）目錄樹與連結 |
| [**docs/templates/page-template-source.md**](docs/templates/page-template-source.md) | `wiki/sources/*` 版型 |
| [**docs/templates/page-template-concept.md**](docs/templates/page-template-concept.md) | `wiki/concepts/*`、`entities/*`、`queries/*` 版型 |

---

## 快速連結

- **給 Agent 複製貼上** → [docs/PROMPTS.md](docs/PROMPTS.md)
- **Skill** → [SKILL.md](SKILL.md) · `/ingest` … `/graph` → [.cursor/skills/](.cursor/skills/)
- **示範 wiki 頁** → [wiki/index.md](wiki/index.md)
- **部門上手** → [docs/onboarding.md](docs/onboarding.md)
