# OKF 對照（主軸）

本 repo 的 `wiki/` 是符合 **[Open Knowledge Format v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)** 的 **Knowledge Bundle**。規格與範例 bundle 見 Google [knowledge-catalog/okf](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)。

維護規約摘要：[**AGENTS.md**](../AGENTS.md) → **OKF 主軸**、**Frontmatter**、**連結規則**、**引用規則**。

---

## Bundle 映射

```text
repo/
├── raw/                    # 本倉擴充：不可變歸檔（不在 OKF bundle 內）
│   ├── sources/
│   └── assets/             # 圖片／附件（.gitkeep 佔位）
└── wiki/                   # OKF Knowledge Bundle 根
    ├── index.md            # OKF 保留檔：目錄（§6）
    ├── log.md              # OKF 保留檔：變更 log（§7）
    ├── sources/            # Concept 子目錄（角色：來源摘要）
    ├── concepts/
    ├── entities/
    ├── queries/
    ├── faq/
    ├── lint/
    └── graph/
```

| OKF | 本倉 |
|-----|------|
| Knowledge Bundle | `wiki/` |
| Concept | 任一 `wiki/**/*.md`（`index.md`、`log.md` 除外） |
| Concept ID | 路徑去 `.md`，相對 `wiki/`（例：`entities/my-service`） |
| 保留檔名 | 僅 `index.md`、`log.md`（[SPEC §3.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)） |

`raw/` 為 **可追溯歸檔** 擴充：Concept 的 `resource` 填 **歸檔 slug** 或外部 URL（見下方 **resource 語意**）；消費端讀 bundle 時無須理解 `raw/` 目錄。

---

## 合規檢查（OKF v0.1）

依 [SPEC §9](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)：

1. 每個非保留 `.md` 含可解析 YAML frontmatter。
2. Frontmatter 含非空 `type`。
3. 若存在 `index.md`／`log.md`，結構符合 §6／§7（本倉 `log.md` 另含操作留痕格式，見 AGENTS）。

消費端 **不得** 因缺少選用欄位、未知 `type`、未知擴充鍵、斷鏈而拒收 bundle——本倉的 `status`、`source_count`、`updated` 屬 producer-defined keys。

---

## Frontmatter 對照

| OKF v0.1 | 本倉慣例 | 備註 |
|----------|----------|------|
| `type`（必填） | `concept` \| `entity` \| `source` \| `query` \| `lint` | OKF 不登錄型別；本倉以 **頁面角色** 作為 `type`。對外可另映射領域型別（見下方匯出） |
| `title`（建議） | 同左 | |
| `description`（建議） | 同左 | 宜與 Summary 首句一致 |
| `resource`（建議） | **歸檔 slug** 或 HTTPS URL | 見下方 **resource 語意**；勿與 bundle 內 `/sources/....md` 路徑混淆 |
| `tags`（建議） | 同左 | |
| `timestamp`（建議） | ISO 8601 | |
| — | `status` | 本倉擴充：審閱狀態 |
| — | `updated` | 本倉擴充：維護日期 |
| — | `source_count` | 本倉擴充：引用計數慣例 |
| `okf_version` | 僅 `wiki/index.md` 可選 | 宣告 `"0.1"`（[SPEC §11](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)） |

### resource 語意（本倉慣例）

OKF `resource` 為底層資產識別。本倉採兩種填法：

| `resource` 值 | 意義 | 範例 |
|---------------|------|------|
| **歸檔 slug** | 對應 `raw/sources/<slug>.md`（不含路徑、不含 `.md`） | `my-api-intro` → `raw/sources/my-api-intro.md` |
| **HTTPS URL** | 外部 canonical URI | `https://api.example.internal/v1` |

* **來源頁**（`type: source`）與綁定實體的 **entity** 頁：優先填歸檔 slug（與歸檔檔名一致，不含副檔名）。
* **抽象 concept** 頁：通常省略 `resource`，或填外部標準文件 URL。
* **Citations** 正文仍寫實際路徑 `../../raw/sources/<slug>.md`（自 `wiki/sources/`），與 frontmatter slug 對照。

範例：來源頁 frontmatter 設 `resource: "my-api-intro"`，對應 `raw/sources/my-api-intro.md` 與 `wiki/sources/my-api-intro.md`。

---

## 連結

### 撰寫（`wiki/` 嵌於 repo — 本範本）

GitHub／IDE **無法** 解析以 `/` 開頭的 OKF bundle 路徑。互連 **一律** 用 **markdown 相對路徑**：

```md
<!-- 自 wiki/concepts/my-concept.md -->
[API 簡介](../sources/my-api-intro.md)
```

| 情境 | 格式 |
|------|------|
| 跨型別子目錄 | `../sources/foo.md`、`../concepts/bar.md` |
| 同子目錄 | `./neighbor.md` |
| 自子目錄連 Index | `../index.md` |
| `wiki/index.md` 列目錄 | `./concepts/foo.md` |
| 歸檔稿（Citations） | `../../raw/sources/<slug>.md`（自 `wiki/sources/`） |

**禁止** `[[concepts/...]]` 與撰寫時的 `/concepts/....md`（除非匯出獨立 bundle）。

### 匯出（獨立 OKF bundle）

將 `wiki/` 打包為 bundle 根時，可將相對連結轉為 OKF 建議的 `/concepts/foo.md` 供 visualize 等工具使用。`resource: "my-api-intro"` 對應 `raw/sources/my-api-intro.md` 與 `wiki/sources/my-api-intro.md`。

---

## 引用（Citations）

| 來源類型 | 作法 |
|----------|------|
| Bundle 內來源 Concept | 相對路徑，例 `../sources/檔名.md` |
| 歸檔稿 | `../../raw/sources/<slug>.md`（自 `wiki/sources/` 等） |
| 外部 URL | 文末 `# Citations` 編號列表（[SPEC §8](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)） |

本倉 **來源頁 Schema**（Summary、Key Concepts…）為 producer 慣例，非 OKF 強制 body 區塊；與 OKF「結構化 markdown body」目標一致。

---

## 匯出／匯入

### 匯出（本倉 → 標準 OKF）

1. 以 `wiki/` 為 bundle 根打包（git／tar）。
2. 確保每 Concept 有 `type`；補齊建議欄位 `title`、`description`、`resource`、`tags`、`timestamp`。
3. 可選：將 `type` 映射為領域字串（例：`entity` + 標籤 `api` → `API Service`）。
4. 匯出獨立 bundle 時，可將相對連結轉為 OKF `/path.md`。
5. 根 `index.md` 可加 `okf_version: "0.1"`。

### 匯入（他方 OKF → 本倉）

1. 將 bundle 置於 `wiki/`（或合併子目錄）。
2. 補本倉擴充：`status`、`updated`、`source_count`；主張須能對應 `wiki/sources/` 或 `# Citations`。
3. 更新 `wiki/index.md`；append `wiki/log.md`。
4. 若需歸檔原始檔，另走 Ingest 寫入 `raw/sources/`（勿改寫既有 `raw/` 檔）。

### 勿為互通而捨棄

* `raw/` 不可變歸檔契約
* 來源頁 Schema 與不確定性標記（AGENTS）
* 操作日誌 append 規則

---

## 參考

* [OKF SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
* [knowledge-catalog/okf README](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
* [Google Cloud 部落格：OKF 介紹](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/)
