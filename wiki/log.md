# Wiki Log

僅可 append 的操作日誌。格式與 pass／no-op 規則見 [AGENTS.md](../AGENTS.md) → **日誌規則**；提示見 [docs/PROMPTS.md](../docs/PROMPTS.md)。

本 repo 的 `wiki/log.md` 留白；fork 後自第一次真實 Ingest／Query 等操作起 append。

## [2026-07-24] reset | 清空知識內容、還原範本骨架

- 已刪除所有 Ingest／Query／Lint／FAQ 知識頁與 `raw/sources`、`raw/assets/*/`、`raw/originals/*`、`raw/inbox/*`（非 `.gitkeep`）內容債。
- 保留：`docs/`、`scripts/`、skills、`AGENTS.md`、目錄 `.gitkeep`、空白 `wiki/index.md`、`wiki/README.md`。
- 自本條起為乾淨範本；後續操作請繼續 append。

## [2026-08-04] ingest | 未收入門_20251217

- 來源：repo 根目錄 `未收入門_20251217.pdf`（14 頁 A4；SHA-256 `2abd46420b643deb4161683a01d6c0283c57666e9b10ed1df3ac4be5eb7cc539`）
- triage：PDF；視覺閘頁 `[2, 4, 5, 6, 7, 8, 9, 10, 11, 13]`；資產皆 `docling_picture` → `raw/assets/未收入門_20251217/pNN.png`
- 轉檔：Docling 初稿 + pdftotext 校正 + vision Visual Evidence
- 新增：`raw/originals/未收入門_20251217.pdf`、`raw/sources/未收入門_20251217.md`
- wiki：`wiki/sources/未收入門_20251217.md`；concepts `催繳`／`墊繳`／`停效`；entity `保費未收作業-AC`；已更新 `wiki/index.md`
- 清理：已刪 repo 根目錄輸入副本 `未收入門_20251217.pdf`（歸檔已在 originals／sources）

## [2026-08-04] ingest | 未收入門_20251217-inbox

- 來源：`raw/inbox/未收入門_20251217.pdf`（14 頁 A4；SHA-256 `2abd46420b643deb4161683a01d6c0283c57666e9b10ed1df3ac4be5eb7cc539`）
- triage：PDF；視覺閘頁 `[2, 4, 5, 6, 7, 8, 9, 10, 11, 13]`；資產皆 `docling_picture` → `raw/assets/未收入門_20251217/pNN.png`
- 轉檔：Docling（`--export-vision-assets`）+ `pdftotext` 校正 + vision Visual Evidence（層／節點盤點＋資料流）
- 新增：`raw/originals/未收入門_20251217.pdf`、`raw/sources/未收入門_20251217.md`
- wiki：更新 `wiki/sources/未收入門_20251217.md`；concepts `催繳`／`墊繳`／`停效`；entity `保費未收作業-AC`（`resource` → `未收入門_20251217`）；已更新 `wiki/index.md`
- 清理：已刪 `raw/inbox/未收入門_20251217.pdf`（歸檔已在 originals／sources）
- lint：`python3 scripts/wiki-lint.py` → ok

## [2026-08-04] ingest | 未收入門_20251217-VE-inline

- 根因：`docs/visual-source-conversion.md` 舊「建議格式」示範文末 `## Visual Evidence` 彙整，導致 Agent 把圖堆在檔案最下面
- 規約修正：放置規則（就地／禁止文末彙整）；更新 PROMPTS／pdf-ingest-sop／AGENTS／ingest Skill
- lint：新增 `Visual Evidence dumped at end`；測試見 `tests/test_wiki_lint_visual_evidence.py`
- 修訂歸檔：新增 `raw/sources/20260804_未收入門_20251217.md`（VE 就地插入各節）；前版 `未收入門_20251217.md` 保留不可變
- wiki：`resource` → `20260804_未收入門_20251217`；已更新 index
- lint：`python3 scripts/wiki-lint.py` → ok

## [2026-08-04] reset | 清空知識內容、還原範本骨架

- 已刪除 Ingest 測試產物：`wiki/sources|concepts|entities` 知識頁；`raw/sources`、`raw/assets/*/`、`raw/originals/*`、`raw/inbox/*`（非 `.gitkeep`）。
- 已還原空白 `wiki/index.md`；清空 `.llm-wiki/usage/events.jsonl`。
- 保留：`docs/`、`scripts/`、`tests/`、skills、`AGENTS.md`、目錄 `.gitkeep`、`wiki/README.md`（含 Visual Evidence 就地放置與 lint 強化）。
- 自本條起為乾淨範本；後續操作請繼續 append。
