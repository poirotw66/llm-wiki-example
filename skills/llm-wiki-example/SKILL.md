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
3. 操作開始／結束自動執行 `python3 scripts/wiki-usage.py start|finish <operation> --title "<title>"`，並 append `wiki/log.md`（實測 token；若漏掉 start，finish 會自動復原且拒絕 0 token；見 `docs/skill-usage.md`）

## 安裝（npx skills）

```bash
npx skills add <owner>/llm-wiki-example --all -a cursor -y
```

本 repo 原始檔位於 `skills/`（**Git 單一來源**）。fork 後請用上方 `npx skills add` 安裝；本機 `.cursor/skills/` 可選、不進 Git。見 [README.md](../../README.md#cursor-skill-用法)。

## 其他

- 上手：docs/onboarding.md · 採用：README.md · OKF：docs/okf.md · 版型：docs/templates/
- `wiki/` 內容留白 — fork 後以 `/ingest` 納入第一份真實來源；`raw/sources/` 寫 **詳盡還原**，`wiki/sources/` 寫 **摘要**
