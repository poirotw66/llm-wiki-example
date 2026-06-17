# OKF Knowledge Bundle（`wiki/`）

`wiki/` 為本 repo 的 **[OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) Knowledge Bundle**。fork 後以 Ingest 填入真實知識；頁面長相見 [docs/templates/](../docs/templates/)。

## 目錄結構

```text
raw/                          # repo 擴充：不可變歸檔（非 bundle 本體）
  sources/
  assets/                     # 圖片／附件
wiki/                         # OKF bundle 根
  index.md                    # okf_version + 總目錄（§6）
  log.md                      # 變更／操作 log（§7 + 本倉擴充）
  sources/                    # Concept：來源摘要
  concepts/
  entities/
  queries/
  faq/
  lint/
  graph/
```

## 進一步閱讀

| 需求 | 檔案 |
|------|------|
| OKF 對照與互通 | [docs/okf.md](../docs/okf.md) |
| 採用與 fork | [README.md](../README.md) |
| 第一輪 Ingest | [docs/onboarding.md](../docs/onboarding.md) |
| 規約 | [AGENTS.md](../AGENTS.md) |
| Agent 提示詞 | [docs/PROMPTS.md](../docs/PROMPTS.md) |
| Skill 總覽 | [skills/llm-wiki-example/](../skills/llm-wiki-example/SKILL.md) |
| 薄 Skill（`/ingest` …） | [skills/](../skills/) 或 [.cursor/skills/](../.cursor/skills/) |
| 來源頁版型 | [page-template-source.md](../docs/templates/page-template-source.md) |
| 概念／實體／Query 版型 | [page-template-concept.md](../docs/templates/page-template-concept.md) |
