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

Fork 後亦可直接使用 [.cursor/skills/](.cursor/skills/)（與 `skills/` 內容同步）。
