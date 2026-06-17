---
name: llm-wiki-example
description: 以來源為根據的 LLM Wiki 部門範本。fork 上手、目錄規約或不知用哪個操作時使用；五大操作請用子 Skill（/ingest、/query、/lint、/faq、/graph）。
---

# llm-wiki-example（總覽 Skill）

## 子 Skill（薄觸發；步驟在 PROMPTS 單一來源）

| 觸發 | Skill 路徑 | 提示詞章節 |
|------|------------|------------|
| `/ingest` | [.cursor/skills/llm-wiki-ingest/SKILL.md](.cursor/skills/llm-wiki-ingest/SKILL.md) | [docs/PROMPTS.md § Ingest](docs/PROMPTS.md) |
| `/query` | [.cursor/skills/llm-wiki-query/SKILL.md](.cursor/skills/llm-wiki-query/SKILL.md) | [docs/PROMPTS.md § Query](docs/PROMPTS.md) |
| `/lint` | [.cursor/skills/llm-wiki-lint/SKILL.md](.cursor/skills/llm-wiki-lint/SKILL.md) | [docs/PROMPTS.md § Lint](docs/PROMPTS.md) |
| `/faq` | [.cursor/skills/llm-wiki-faq/SKILL.md](.cursor/skills/llm-wiki-faq/SKILL.md) | [docs/PROMPTS.md § FAQ](docs/PROMPTS.md) |
| `/graph` | [.cursor/skills/llm-wiki-graph/SKILL.md](.cursor/skills/llm-wiki-graph/SKILL.md) | [docs/PROMPTS.md § Graph](docs/PROMPTS.md) |

**維護原則**：操作步驟只改 [docs/PROMPTS.md](docs/PROMPTS.md)；規約只改 [AGENTS.md](AGENTS.md)。子 Skill 勿複製長步驟。

## 三步（任何操作）

1. [AGENTS.md](AGENTS.md) — 硬約束與操作定義  
2. [docs/PROMPTS.md](docs/PROMPTS.md) — 對應章節全文執行  
3. `wiki/index.md`（若適用）+ append `wiki/log.md`

## 其他

- 上手：[docs/onboarding.md](docs/onboarding.md) · 採用：[README.md](README.md) · OKF：[docs/okf.md](docs/okf.md)（[SPEC](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)）
- 本倉含 **虛構示範頁**（`範例` 標籤）；fork 後請刪除或覆寫
