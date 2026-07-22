---
name: llm-wiki-example-readme
description: 內部說明；可安裝 Skill 見 skills/ 目錄。
metadata:
  internal: true
---

# Skill 安裝說明

可安裝的 Skill 位於 **[skills/](skills/)**（[vercel-labs/skills](https://www.npmjs.com/package/skills) 標準格式）。

```bash
# Cursor + Claude Code + Codex（本專案）
npx skills add <owner>/llm-wiki-example -a cursor -a claude-code -a codex -y

# 全域（本機所有專案）
npx skills add <owner>/llm-wiki-example -a cursor -a claude-code -a codex -g -y

# 本 repo 全部 Skill → 所有偵測到的 Agent
npx skills add <owner>/llm-wiki-example --all -y

# 本地開發（於 repo 根目錄）
npx skills add . --all -a cursor -y
```

總覽與觸發表見 [skills/llm-wiki-example/SKILL.md](skills/llm-wiki-example/SKILL.md) 與 [README.md](README.md#cursor-skill-用法)。

Skill **以 [`skills/`](skills/) 為 Git 單一來源**。fork 後請用上方 `npx skills add` 安裝到 Cursor／Claude Code／Codex；本機可選副本 `.cursor/skills/` **不進遠端**（見 [`.gitignore`](.gitignore)）。
