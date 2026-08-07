# OKF Knowledge Bundle（`wiki/`）

`wiki/` 為本 repo 的 **[OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) Knowledge Bundle**。fork 後以 Ingest 填入真實知識；頁面長相見 [docs/templates/](../docs/templates/)。寫入或分享前須先通過 [企業資料治理](../docs/data-governance.md)。

## 目錄結構

```text
raw/                          # repo 擴充：不可變歸檔（非 bundle 本體）
  inbox/                      # 待處理原件
  originals/                  # 所有輸入原件（含 MD）
  sources/                    # canonical Markdown 歸檔稿
  assets/                     # 視覺附件
wiki/                         # OKF bundle 根
  index.md                    # okf_version + 總目錄（§8）
  purpose.md                  # 方向（目標／關鍵問題／範圍）
  review/queue.md             # 非同步人審佇列
  log.md                      # 變更／操作 log（§9 + 本倉擴充）
  sources/                    # Concept：來源摘要
  concepts/
  entities/
  queries/
  faq/
  lint/
  graph/                      # knowledge-map（選用）、insights.md（結構洞見）
```

## 進一步閱讀

| 需求 | 檔案 |
|------|------|
| OKF 對照與互通 | [docs/okf.md](../docs/okf.md) |
| 採用與 fork | [README.md](../README.md) |
| 第一輪 Ingest | [docs/onboarding.md](../docs/onboarding.md) |
| Ingest 管線 | [docs/ingest-pipeline.md](../docs/ingest-pipeline.md) |
| Wiki lint | `uv run --group test python3 scripts/wiki-lint.py` |
| PDF 轉譯 SOP | [docs/pdf-ingest-sop.md](../docs/pdf-ingest-sop.md) |
| 規約 | [AGENTS.md](../AGENTS.md) |
| Agent 提示詞 | [docs/PROMPTS.md](../docs/PROMPTS.md) |
| Skill 總覽 | [skills/llm-wiki-example/](../skills/llm-wiki-example/SKILL.md) |
| 薄 Skill（`/ingest` …） | [skills/](../skills/)（Git 來源；Cursor 用 `npx skills add`，見 [README](../README.md#cursor-skill-用法)） |
| 來源頁版型 | [page-template-source.md](../docs/templates/page-template-source.md) |
| 概念／實體／Query 版型 | [page-template-concept.md](../docs/templates/page-template-concept.md) |
