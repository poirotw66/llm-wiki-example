# OKF v0.2 對照、治理與互通

本 repo 的 `wiki/` 是純 **[Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)** Knowledge Bundle；`raw/` 與企業治理規則是本倉擴充。完整決策見 [AGENTS.md](../AGENTS.md) 與 [data-governance.md](./data-governance.md)。

## Bundle 映射

```text
repo/
├── raw/                    # 本倉擴充；不可變歸檔，非 bundle 本體
│   ├── inbox/              # 待處理原件（僅通過治理閘後）
│   ├── originals/          # 已准入的輸入原件位元副本
│   ├── sources/            # canonical Markdown 歸檔稿
│   └── assets/             # 視覺附件
└── wiki/                   # OKF Knowledge Bundle 根
    ├── index.md            # OKF 保留檔；可宣告 okf_version: "0.2"
    ├── log.md              # OKF 保留檔；本倉另有操作留痕
    └── sources/ concepts/ entities/ queries/ faq/ lint/ graph/
```

| OKF | 本倉 |
|---|---|
| Knowledge Bundle | `wiki/` |
| Concept | 任一 `wiki/**/*.md`（`index.md`、`log.md`、`purpose.md`、`queue.md`、`insights.md`、`README.md` 除外） |
| Concept ID | 相對 `wiki/` 的路徑去掉 `.md` |
| `index.md`／`log.md` | 任意層級的保留檔名，不能作 Concept |

## 合規與 v0.2 frontmatter

OKF v0.2 的 Concept 核心要求是可解析 YAML frontmatter 與非空 `type`；保留檔存在時亦須符合 index／log 結構。未知欄位、未知 type、缺少選用家族或斷鏈不能使一般 consumer 拒收。本範例作為 producer 採更嚴格的規則：固定宣告 `okf_version: "0.2"`，並要求 provenance、lifecycle 與治理欄位通過 lint。

| 家族 | 欄位 | 本倉決策 |
|---|---|---|
| 核心 | `type` | 必填；現行角色型別 `concept`、`entity`、`source`、`query`、`lint` 保留。 |
| 核心 | `title`、`description`、`resource`、`tags` | 建議；`resource` 應為 URI 或 path，不把單獨 slug 當作新內容的 URI。 |
| provenance | `sources`、`usage_window` | 新內容必填 `sources`（每項 `resource` 必填）；可加 `id`、`title`、`author`、`usage_count`、`last_modified`。 |
| trust | `generated`、`verified` | 新內容必填 `generated.by`／`generated.at`；人工覆核才可寫 `verified` 的 `human:<id>`。 |
| lifecycle | `status`、`stale_after` | 新內容的 `status` 用 `draft`、`stable`、`deprecated`；需要期限時填絕對日期。 |
| governance extension | `classification`、`owner`、`access_scope`、`contains_pii`、`retention`、`redaction` | 新內容必填；完整 enum 與 Git 准入見 [data-governance.md](./data-governance.md)。 |

```yaml
---
type: concept
title: "<Page title>"
description: "<一語摘要>"
resource: "https://example.com/canonical-resource"
tags: []
sources:
  - id: source-1
    resource: "../sources/<source-page>.md"
    title: "<來源標題>"
generated: { by: "agent/model-version", at: "YYYY-MM-DDTHH:MM:SSZ" }
status: draft
stale_after: "YYYY-MM-DD"
classification: internal
owner: "team:<id>"
access_scope: "team:<id>"
contains_pii: false
retention: "per-policy:<id>"
redaction: none
---
```

`generated.by`／`verified[].by` 僅接受 `agent-or-tool/version`、`human:<id>`、`process:<id>` 的 actor 慣例。`verified` 可為單一 mapping 或事件 list；無 `verified` 是 unverified，只有非 human actor 是 machine-confirmed，含 `human:` 才是 human-reviewed。這些是信任訊號，不是 access control。

### `resource` 與歸檔

來源頁以 `archive_slug: "<slug>"` 作本倉 extension 對應 `raw/sources/<slug>.md`；OKF `resource` 必須是 underlying asset 的 URI 或可解析 path，不能填 bare slug。若 canonical 僅在本 repo，將 `../../raw/sources/<slug>.md` 放在 `sources[].resource`；匯出獨立 bundle 前，改為可分發的外部 URI 或將材料納入 bundle 的 `references/`。

## 歸因、連結與索引

逐項主張使用與 `sources[].id` 相同的 footnote label：

```md
此主張由官方規格支持。[^okf-spec]

[^okf-spec]: Open Knowledge Format specification
```

```yaml
sources:
  - id: okf-spec
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
    title: Open Knowledge Format specification
```

本 repo 中，Concept 間仍用 markdown 相對連結，避免 GitHub／IDE 將 `/path.md` 解為 repo／網站根。獨立 bundle 匯出時可轉為 v0.2 建議的 `/path.md`。根 `wiki/index.md` 是唯一可帶 frontmatter 的 index，僅可含 `okf_version: "0.2"`。

## 匯入、匯出與治理 gate

匯入其他 bundle 前必須先正規化為 v0.2；不可臆造 `generated.by`、`verified` 或來源信號。匯出前應：

1. 檢查每個 Concept 的 `type` 與 YAML。
2. 確認所有頁使用 `sources`、`generated`、v0.2 lifecycle 與治理欄位。
3. 移除或轉換指向 repo 外 `raw/` 的相對來源，讓 bundle 可攜。
4. 依 [data-governance.md](./data-governance.md) 重新判斷 classification、PII、redaction 與 Git／分享准入。

`raw/` 不可變契約、來源頁 Schema、相對連結與 append-only 操作日誌在互通時仍保留；但它們不會因 OKF 宣告而自動獲得 Git 或外部分享授權。

## 參考

* [OKF v0.2 SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
* [knowledge-catalog/okf](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
