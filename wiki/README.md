# LLM Wiki（llm-wiki-example）

`wiki/` 為知識庫本體（目前為**空骨架**）。各部門請 **fork／Template** 專用 repo 後再寫入內容。

## 目錄結構

```text
raw/
  sources/    # 歸檔來源（新增檔；既有檔不就地修改）
  assets/     # 圖片／附件（選用）
wiki/
  sources/
  concepts/
  entities/
  queries/
  faq/
  lint/
  graph/      # 選用
  index.md    # 總目錄
  log.md      # 操作日誌（僅 append）
```

## 進一步閱讀

| 需求 | 檔案 |
|------|------|
| 採用與 fork | 根目錄 [README.md](../README.md) |
| 第一輪 Ingest 假資料流程 | [docs/onboarding.md](../docs/onboarding.md) |
| 規約、命名、連結、操作與 Agent 提示 | [AGENTS.md](../AGENTS.md) |
| `wiki/sources/*` 起稿版型 | [docs/templates/page-template-source.md](../docs/templates/page-template-source.md) |
