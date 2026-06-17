# llm-wiki-example（LLM Wiki 範例工作區）

供各部門 **fork／GitHub Template** 後自建 wiki 的 **空白起步 repo**：`raw/`、`wiki/`、[`wiki/index.md`](wiki/index.md)、[`wiki/log.md`](wiki/log.md) 與版型已就位。規約與 Agent 操作提示皆在 [**AGENTS.md**](AGENTS.md)（單一來源）。

---

## 採用指南（給各部門）

本 repo 是 **範本**，不是各部門共用的知識庫。

### 三步開始

1. **建立部門專用 repo** — 使用 **Use this template** 或 fork 後改名；**勿**在本 example 倉寫部門內容。  
2. **客製化** — 編輯 [`wiki/index.md`](wiki/index.md) 的 **Overview**（部門、範圍、維護者）；必要時微調 [**AGENTS.md**](AGENTS.md)。  
3. **第一次 Ingest** — 先讀 [**docs/onboarding.md**](docs/onboarding.md)（虛構流程，不寫入本倉 `wiki/`）；實作時依 **AGENTS.md** 的 **Operations Prompts（複製貼上）** 請 Agent 執行。

### 日常在做什麼

| 操作 | 何時用 |
|------|--------|
| **Ingest** | 新文件／規格要納入 wiki |
| **Query** | 向 wiki 提問（可重用答案寫入 `wiki/queries/`） |
| **Lint** | 定期或 PR 前檢查品質 |
| **FAQ** / **Graph** | 主題夠多或關係複雜時（進階） |

步驟、格式、硬約束（引用、`raw/` 不可變、一律 append log 等）→ [**AGENTS.md**](AGENTS.md)。

---

## 專案目的

建立 **以來源為根據、可追溯、可連結演進** 的 Markdown 知識庫，供 LLM／人類維護，並支援 FAQ、onboarding、RAG、Agent。核心取向：有來源才寫入、結構化分頁、頁面互連、操作留 log。

---

## 文件地圖

| 檔案 | 用途 |
|------|------|
| [**AGENTS.md**](AGENTS.md) | 目錄契約、頁面格式、五大操作、**Operations Prompts** |
| [**docs/onboarding.md**](docs/onboarding.md) | 第一輪 Ingest 假資料 walkthrough |
| [**wiki/README.md**](wiki/README.md) | `wiki/` 目錄說明、命名與連結慣例 |
| [**docs/templates/page-template-source.md**](docs/templates/page-template-source.md) | `wiki/sources/*` 起稿版型 |

---

## 快速連結

- **給 Agent 複製貼上** → [AGENTS.md § Operations Prompts](AGENTS.md)
- **部門上手** → [docs/onboarding.md](docs/onboarding.md)
- **wiki 資料夾** → [wiki/README.md](wiki/README.md)
