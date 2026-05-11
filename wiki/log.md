# Wiki Log

Chronological, append-only operational log.

## [2026-05-06] bootstrap | Initialize empty LLM Wiki under example/

- 建立 `example/raw/sources`、`example/raw/assets` 與 `example/wiki/*` 分層（sources、concepts、entities、queries、faq、lint、graph）。
- 初始化 `wiki/index.md`（空目錄）、`wiki/log.md`。
- 複製 **AGENTS.md** 至 `example/AGENTS.md`；複製頁面版型至 `example/docs/templates/page-template.md`。

## [2026-05-08] docs | Restore docs/ mirror under example/

- 主倉 **`docs/`** 已復原；**example/docs/templates/page-template.md** 與主倉版型同步；Agent 全文 prompt 請用主倉 **docs/OPERATIONS.md**。
