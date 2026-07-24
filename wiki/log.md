# Wiki Log

僅可 append 的操作日誌。格式與 pass／no-op 規則見 [AGENTS.md](../AGENTS.md) → **日誌規則**；提示見 [docs/PROMPTS.md](../docs/PROMPTS.md)。

本 repo 的 `wiki/log.md` 留白；fork 後自第一次真實 Ingest／Query 等操作起 append。

## [2026-07-24] reset | 清空知識內容、還原範本骨架

- 已刪除所有 Ingest／Query／Lint 知識頁與 `raw/sources`、`raw/assets/*/`、`raw/originals/*` 內容債。
- 保留：`docs/`、`scripts/`、skills、`AGENTS.md`、目錄 `.gitkeep`、空白 `wiki/index.md`；規約已含「MD 亦入 `raw/originals/`」。
- 自本條起為乾淨範本；後續操作請繼續 append。
