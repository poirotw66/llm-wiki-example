# LLM Wiki（Example）

Persistent, LLM-maintained knowledge base in markdown（空骨架）。

## Folder Layout

```text
raw/
  sources/    # archived sources（新增歸檔；既有檔不就地修改）
  assets/     # images / attachments（選用）
wiki/
  sources/
  entities/
  concepts/
  queries/
  faq/
  lint/
  graph/
  index.md
  log.md
AGENTS.md     # 本 example 內複本，規約以此為準
```

## Quick Start

1. 提供 **指定**來源檔或將稿件 **歸檔**為 `raw/sources/` 下之 **新檔** `*.md`。  
2. 依 **AGENTS.md** 執行 Ingest（wiki/sources、concepts、entities、index、log）。  
3. 確認 `wiki/index.md` 已列出條目，`wiki/log.md` 已 append。

## Naming Suggestions

- Source page: `wiki/sources/<source-slug>.md`
- Entity page: `wiki/entities/<entity-name>.md`
- Concept page: `wiki/concepts/<concept-name>.md`
- Query page: `wiki/queries/<query-slug>.md`
- FAQ page: `wiki/faq/<faq-slug>.md`

## Editing Discipline

- Do not change **existing** files under `raw/` in place; add new archives during Ingest.
