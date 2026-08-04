# Wiki Log

僅可 append 的操作日誌。格式與 pass／no-op 規則見 [AGENTS.md](../AGENTS.md) → **日誌規則**；提示見 [docs/PROMPTS.md](../docs/PROMPTS.md)。

本 repo 的 `wiki/log.md` 留白；fork 後自第一次真實 Ingest／Query 等操作起 append。

## [2026-08-04] lint | 企業內部 LLM Wiki 架構與功能審查

- 自動 lint：`python3 scripts/wiki-lint.py` → pass；測試：以臨時 `pytest`／Pillow 環境執行 → 7 passed。
- 深度檢查：發現 OKF v0.2 版本漂移、企業資料治理缺口、ingest cleanup 刪除邊界不足、frontmatter 非真正 YAML 解析、CI／測試依賴缺口，以及規約與實作覆蓋不一致。
- 本次僅審查，未新增 `wiki/lint/` 產物、未修改知識頁或 index。
