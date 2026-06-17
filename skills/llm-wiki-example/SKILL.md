---
name: llm-wiki-example
description: 以來源為根據的 LLM Wiki 部門範本。fork 上手、目錄規約或不知用哪個操作時使用；五大操作請用子 Skill（/ingest、/query、/lint、/faq、/graph）。
---

# llm-wiki-example（總覽 Skill）

## 子 Skill（薄觸發；步驟在 PROMPTS 單一來源）

| 觸發 | Skill 名稱 | 提示詞章節 |
|------|------------|------------|
| `/ingest` | `llm-wiki-ingest` | docs/PROMPTS.md § Ingest |
| `/query` | `llm-wiki-query` | docs/PROMPTS.md § Query |
| `/lint` | `llm-wiki-lint` | docs/PROMPTS.md § Lint |
| `/faq` | `llm-wiki-faq` | docs/PROMPTS.md § FAQ |
| `/graph` | `llm-wiki-graph` | docs/PROMPTS.md § Graph |

**維護原則**：操作步驟只改工作區根目錄 **docs/PROMPTS.md**；規約只改 **AGENTS.md**。子 Skill 勿複製長步驟。

## 三步（任何操作）

1. **AGENTS.md** — 硬約束與操作定義
2. **docs/PROMPTS.md** — 對應章節全文執行
3. `wiki/index.md`（若適用）+ append `wiki/log.md`

## 安裝（npx skills）

```bash
npx skills add <owner>/llm-wiki-example --all -a cursor -y
```

本 repo 原始檔位於 `skills/`；亦可 fork 後直接使用 `.cursor/skills/`。

## 其他

- 上手：docs/onboarding.md · 採用：README.md · OKF：docs/okf.md
- 本倉含 **虛構示範頁**（`範例` 標籤）；fork 後請刪除或覆寫
