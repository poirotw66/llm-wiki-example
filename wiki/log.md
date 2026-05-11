# Wiki Log

Chronological, append-only operational log.

## [2026-05-06] bootstrap | Initialize empty LLM Wiki repository

- 建立 `raw/sources`、`raw/assets` 與 `wiki/*` 分層（sources、concepts、entities、queries、faq、lint、graph）。
- 初始化 `wiki/index.md`（空目錄）、`wiki/log.md`。
- 放置 **AGENTS.md** 於 repo 根目錄；頁面版型於 `docs/templates/page-template.md`。

## [2026-05-08] docs | Restore docs/ in this repository

- 本倉 **`docs/`** 已就緒；`docs/templates/page-template.md` 與版型約定對齊；Agent 操作複製提示以本倉 **docs/OPERATIONS.md** 為準。

## [2026-05-11] docs | Align README / index / log with standalone repo

- 敘述改為本 repo **llm-wiki-example** 即主工作區，移除「example 子資料夾」「上一層主倉」等易誤導路徑；**docs/OPERATIONS.md** 統一為本倉權威操作提示；同步修正 **wiki/README.md** 標題與 AGENTS.md 說明。

## [2026-05-11] hygiene | .gitignore and graphify scope

- **.gitignore**：改為 `**/.DS_Store`；新增 `graphify-out/`（本倉不納入 graphify 產物，本機產生者不提交）。
- **README.md**：新增「Graphify 與 `graphify-out/`」小節，對照 Cursor 規則中可能引用之不存在路徑。

## [2026-05-11] docs | Source template split and OPERATIONS coverage

- **docs/templates**：`page-template.md` 改為索引；新增 **page-template-source.md**（對齊 **AGENTS.md** Source Page Schema 區塊名稱）、**page-template-concept.md**（非 source 頁）；**AGENTS.md** 目錄契約與 Source 版型句同步更新。
- **docs/OPERATIONS.md**：補 **FAQ**、**Graph**、**Wiki log append (pass / no-op)** 英文複製提示；Lint／總述對齊「每次執行須 append `wiki/log.md`」規則。
