# Wiki Log

僅可 append 的操作日誌。格式與 pass／no-op 規則見 [AGENTS.md](../AGENTS.md) → **日誌規則**；提示見 [docs/PROMPTS.md](../docs/PROMPTS.md)。

本 repo 的 `wiki/log.md` 留白；fork 後自第一次真實 Ingest／Query 等操作起 append。

## 2026-08-04

- **lint** | 企業內部 LLM Wiki 架構與功能審查
  - 自動 lint：`python3 scripts/wiki-lint.py` → pass；測試：以臨時 `pytest`／Pillow 環境執行 → 7 passed。
  - 深度檢查：發現 OKF v0.2 版本漂移、企業資料治理缺口、ingest cleanup 刪除邊界不足、frontmatter 非真正 YAML 解析、CI／測試依賴缺口，以及規約與實作覆蓋不一致。
  - 本次僅審查，未新增 `wiki/lint/` 產物、未修改知識頁或 index。

## 2026-08-05

- **lint** | 企業治理與 OKF v0.2 生產化強化
  - 完成資料治理規約、OKF v0.2 非破壞遷移、cleanup allowlist／SHA-256／`--confirm` 防呆、真正 YAML/schema lint 與 GitHub Actions CI。
  - 新增 lint 報告與 index 連結；完整測試、wiki lint 與 diff 檢查通過。

- **lint** | 全面移除 OKF v0.1 相容語法
  - 將唯一舊格式 log 完整重排為 v0.2 日期分組，並移除規約、模板、parser 與 resource slug 的舊格式相容分支。
  - lint 現會拒絕非 v0.2 metadata、lifecycle、Citations、bare resource slug、舊版 index 與 bracket heading；31 項測試通過。
