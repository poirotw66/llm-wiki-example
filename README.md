# llm-wiki-example（LLM Wiki 範例工作區）

本倉庫 **llm-wiki-example** 為獨立 repo，依 [**AGENTS.md**](AGENTS.md) 規約建立的 **空白 LLM Wiki 起步結構**：含 `raw/`、`wiki/` 目錄契約、`wiki/index.md` 總目錄與 `wiki/log.md`，尚未含任何知識頁。

## 下一步

1. 將來源檔依 **AGENTS.md** Ingest：`指定檔 → 歸檔至 `raw/sources/*.md` → 更新 `wiki/sources/*`、concepts／entities… → `wiki/index.md` → append `wiki/log.md`。  
2. 頁面版型索引：[docs/templates/page-template.md](docs/templates/page-template.md)（由此選用 **source**／**concept** 等版型）；Agent 操作步驟與複製提示以本倉 [**docs/OPERATIONS.md**](docs/OPERATIONS.md) 為準。

## Graphify 與 `graphify-out/`

本範例 **不納入** graphify 類工具之產物目錄（例如 `graphify-out/GRAPH_REPORT.md`）。若你本機安裝 graphify 並執行分析，產物會落在 `graphify-out/`（已列於 [.gitignore](.gitignore)，不會誤提交）。部分 Cursor 工作區規則若提及讀取 `graphify-out/`，在本倉可能**不存在該路徑**，屬預期；可改以 `wiki/index.md`、原始碼與 **AGENTS.md** 為架構參考，或於本機產生 graphify 報告後再讀。
