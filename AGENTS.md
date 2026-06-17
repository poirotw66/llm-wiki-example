# 📘 LLM Wiki 規約

你是本 wiki 的維護者。請將此 repository 視為 **持久、偏圖結構（graph-aware）、以來源為根據（source-grounded）** 的知識系統。

---

# 🎯 系統目標

建立 **可自我演進的知識庫**，使其：

* 降低幻覺
* 提高可追溯性
* 維持結構化關係（graph）
* 支援重用（FAQ、onboarding、RAG、agents）

---

# 🧠 核心原則

* 以來源為根據 ＞ 臆測
* 結構 ＞ 篇幅
* 連結 ＞ 孤立
* 演進 ＞ 一次完美

---

# 📦 OKF 主軸

本倉以 **[Open Knowledge Format（OKF）v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)** 為知識表示主軸（參考 [knowledge-catalog/okf](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)）。`wiki/` 即 **Knowledge Bundle**；其餘目錄與操作規則為在 OKF 之上的 **本倉擴充**（可追溯歸檔、Agent 維護流程）。

| OKF 術語 | 本倉對應 |
|----------|----------|
| Knowledge Bundle | `wiki/` |
| Concept | `wiki/**/*.md`（保留檔名 `index.md`、`log.md` 除外） |
| Concept ID | 相對 `wiki/` 之路徑去掉 `.md`（例：`concepts/rest-api`） |
| `index.md` | `wiki/index.md`（漸進式揭露總目錄） |
| `log.md` | `wiki/log.md`（變更歷史；本倉另訂操作日誌格式） |

**OKF 合規（v0.1）**：每個 Concept 須有可解析 YAML frontmatter，且含非空 `type`。其餘約束見下方 Frontmatter 與 [**docs/okf.md**](docs/okf.md)。

**本倉擴充（不違反 OKF 消費端容忍未知鍵）**：`raw/` 不可變歸檔、`status`／`source_count`／`updated`、來源頁 Schema、五大操作與 `wiki/log.md` 操作留痕。

---

# 📁 目錄契約

* `raw/`：既有來源的 **不可變** 區（❗ 不可就地修改）。**Ingest** 第二步可將 **新** 檔 **歸檔** 至 `raw/sources/`。

* `raw/assets/`：選用之圖片／附件，由來源或 wiki 頁引用（不解析為知識頁；Ingest 或維護時視需要新增）。

* `wiki/`：**OKF Knowledge Bundle**（由 LLM／人類維護的知識本體）

* `wiki/index.md`：總目錄（canonical catalog）

* `wiki/log.md`：僅可 append 的操作日誌

* `wiki/sources/`：自來源整理之知識頁

* `wiki/concepts/`：抽象概念（MVC、API、Transaction）

* `wiki/entities/`：具體系統（Vue、Spring Boot、JDBC）

* `wiki/queries/`：可重用之 **單一** 問答頁（一題 → 一則持久化答案）

* `wiki/faq/`：結構化 **FAQ 題組**（每頁 8–15 題；frontmatter `type: query` 且 `tags: ["faq"]` — `type` 表示頁面形狀，非 `wiki/queries/` 資料夾）

* `wiki/lint/`：診斷／檢查結果

* `wiki/graph/`：關係對照（選用、進階）

* `docs/`（**支援文件**，不計入 wiki 知識本體）：

  * `docs/templates/page-template-source.md` — 僅供 **`wiki/sources/*`** 起稿；區塊標題須與下方 **來源頁 Schema** 完全一致。

  * `docs/onboarding.md` — 第一輪 Ingest 解說；與本倉 **wiki 虛構示範頁** 對照。

  * `docs/PROMPTS.md` — **Operations Prompts（複製貼上）** 與範例指令；Agent **操作步驟**之唯一維護來源。

  * `docs/okf.md` — **OKF v0.1 對照與互通**（bundle 映射、欄位、連結、匯出）；規格原文見 [SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)。

  * `SKILL.md`（repo 根）— 總覽 Skill；指向子 Skill 與三步流程。

  * `.cursor/skills/llm-wiki-{ingest,query,lint,faq,graph}/` — **薄 Skill**（觸發 `/ingest` 等）；委派 `docs/PROMPTS.md` 對應章節，勿複製長步驟。

### 目錄設計：型別式子目錄（OKF 相容）

OKF **不**規定固定分類法；子目錄僅為組織 Concept 之用（[SPEC §3](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)）。本倉採 **`sources`／`concepts`／`entities`** 等 **知識角色** 分層，而非 `wiki/<topic>/` 純主題目錄——以利 Ingest 落點、Schema 檢查與 Agent 操作。規模變大時可在型別下加領域子目錄（例如 `wiki/entities/訂單/訂單服務.md`），無須改為純主題式。

---

# 🧱 Wiki 頁面約定

* 僅 Markdown

* 除 `wiki/index.md`（bundle 根 index，frontmatter 僅可選 `okf_version`）外，每個 Concept 須含 YAML frontmatter（見 **Frontmatter（OKF + 本倉擴充）**）

* 語言：**繁體中文**

* 技術名詞保留英文（API、MVC、Vue…）

* 文風：

  * 簡潔
  * 結構化
  * 可驗證

* **檔案與路徑命名**（`wiki/**`、Ingest 新增之 `raw/sources/*.md` 等由本 wiki 決定之檔名）：

  * 使用**繁體中文**或**英文**（含技術詞、既有目錄沿用之 slug，例如 `concepts/api`）。
  * **勿**以**漢語拼音**拼寫中文語意作為檔名或路徑片段：對台灣讀者不直觀，也與本地慣用之書寫系統不一致；應改為繁體字面，或改用具辨識度之英文識別名。

---

# 📌 Frontmatter（OKF + 本倉擴充）

每個 **Concept**（`wiki/**/*.md`，保留檔名除外）須含 YAML frontmatter。

### OKF v0.1（規格層）

| 層級 | 鍵 | 說明 |
|------|-----|------|
| **必填** | `type` | 概念種類；本倉慣用 `concept`、`entity`、`source`、`query`、`lint`（亦符合 OKF「自描述型別字串」） |
| **建議** | `title` | 顯示名稱 |
| **建議** | `description` | 一語摘要（index、搜尋預覽） |
| **建議** | `resource` | 底層資產 URI；來源頁指向 `raw/sources/...` 或原始 URL |
| **建議** | `tags` | 標籤列表 |
| **建議** | `timestamp` | ISO 8601 最後有意義變更時間 |

規格與範例見 [OKF SPEC §4.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)。

### 本倉擴充（維護層）

| 鍵 | 說明 |
|-----|------|
| `status` | `draft` \| `active` \| `needs-review` |
| `updated` | 維護用日期 `YYYY-MM-DD`（可與 `timestamp` 並存） |
| `source_count` | 引用之來源 concept 數（慣例） |

```yaml
---
type: concept
title: "<Page title>"
description: "<一語摘要>"
resource: "<URL 或 raw/sources/...>"
tags: []
timestamp: "YYYY-MM-DDTHH:MM:SSZ"
status: "<draft|active|needs-review>"
updated: "YYYY-MM-DD"
source_count: 0
---
```

互通對照與匯出映射見 **`docs/okf.md`**。

### `wiki/index.md`（bundle 根 index）

* 依 OKF [§6](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)，**一般不含 frontmatter**；本檔亦 **可不** 加 YAML。
* 若宣告目標 OKF 版本，**僅** 可在 bundle 根 `index.md` 加 `okf_version: "0.1"`（[§11](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)）；其餘 frontmatter 鍵非 OKF 標準。
* 必要結構為下方 **索引結構** 標題排版（`# Index`、`## Overview`…）；缺 frontmatter 不視為不合規。
* schema 中 `type: "overview"` 供團隊自訂之獨立概覽頁（例如 `wiki/overview.md`）；**非** `wiki/index.md` 必填。

---

# 🔗 連結規則（強制）

* 每頁至少連結 ≥1 頁（OKF 跨頁關係；見 [SPEC §5](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)）
* 每個新頁須被別處引用
* 盡量雙向連結

### OKF 連結（互通首選）

Bundle 內 Concept 互連時，OKF **建議** bundle 根相對絕對路徑（以 `/` 開頭、含 `.md`）：

```md
見 [REST API](/concepts/rest-api.md)。
```

### Wiki 撰寫慣例（本倉）

內文可使用 wiki 式連結，不含 `wiki/` 前綴，語意等同 OKF bundle 內路徑：

* `[[sources/example]]` ↔ `/sources/example.md`
* `[[concepts/api]]` ↔ `/concepts/api.md`
* `[[entities/spring-boot]]` ↔ `/entities/spring-boot.md`

路徑相對於 `wiki/` 解析。匯出至他方 OKF 工具時，應轉為標準 markdown 連結（見 **`docs/okf.md`**）。

自 wiki 頁連至總目錄或支援文件時，`[[../index]]`（即 `wiki/index.md`）以及 repo 根 **`AGENTS.md`**、**`docs/PROMPTS.md`**、**`docs/onboarding.md`**、**`SKILL.md`** 均為有效目標。

### 冷啟動（空白 wiki）

* 第一則知識頁建立前，骨架無 wiki 頁可互連。**第一次 Ingest 後**，每個新頁至少連結一個其他 wiki 頁（通常經 `[[../index]]` 連至 `wiki/index.md`，或 source／concept／entity 頁互連）。

---

# 🧩 知識圖規則

每頁應隱含或明確定義關係：

### 允許的關係

* `concept → concept`
* `concept → entity`
* `entity → concept`
* `source → concept/entity`

### 可選的明確區塊：

```md
## Relationships

- related_to: [[concepts/api]]
- implemented_by: [[entities/spring-boot]]
- used_in: [[sources/ch1]]
```

👉 供日後 graph 推理（RAG／agents）

---

# 📏 頁面粒度規則

* 一頁 = 一概念或一實體
* 超過 500 字 → 拆分
* 不可混用不同抽象層次

---

# 📌 引用規則（關鍵）

* 所有可驗證主張須引用來源（與 OKF [§8 Citations](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) 一致）

**Bundle 內來源 Concept**（慣例）：

```md
[[sources/ch1]]
```

或 OKF 形式：`[ch1](/sources/ch1.md)`

**外部 URL**：建議在文末加 `# Citations` 區塊（編號列表），例如：

```md
# Citations

[1] [官方文件](https://example.com/docs)
```

多個 bundle 內來源：

```md
[[sources/ch1]], [[sources/ch3]]
```

---

# ⚠️ 不確定性標記

* （確定）
* （推測）
* （未知）

---

# 📚 來源頁 Schema

每個 `wiki/sources/*` 須包含：

```md
## Summary
- 3–5 bullets

## Key Concepts

## Entities

## Notable Claims

## Limitations / Gaps
```

來源頁起稿版型：**`docs/templates/page-template-source.md`**。

---

# 📄 Concept／Entity／Query／Lint 頁（建議骨架）

**`wiki/concepts/*`**、**`wiki/entities/*`**、**`wiki/queries/*`**、**`wiki/lint/*`**：使用 **必填 Frontmatter**；下列區塊名稱為 **建議**（不如 **來源頁 Schema** 嚴格）。`type` 設為 `concept` | `entity` | `query` | `lint`。有根據的主張須引用來源。

```yaml
---
type: concept
title: "<Page title>"
description: "<一語摘要>"
resource: "<URL 或 raw/sources/...>"
tags: []
timestamp: "YYYY-MM-DDTHH:MM:SSZ"
status: draft
updated: "YYYY-MM-DD"
source_count: 1
---
```

```md
# <Page title>

## Summary

一段概述。

## Key Points

- 要點並引用 [[sources/...]]

## Evidence

- 有根據的主張 → [[sources/...]] 或 `raw/sources/*`

## Relationships

- related_to: [[concepts/...]]
- implemented_by: [[entities/...]]

## Open Questions

- 待釐清事項（選填）
```

`wiki/faq/` 使用下方 **FAQ 頁格式**（非本骨架）。實例見 **`wiki/concepts/rest-api.md`**、**`wiki/entities/訂單服務.md`**（標籤 `範例`）及 **`docs/onboarding.md`**。

---

# 📑 索引結構

總目錄為 **`wiki/index.md`**（單一檔）。除非團隊慣例另建 `wiki/overview.md`，否則 **下列各節（含 Overview）皆在 `wiki/index.md`**，順序如下：

```md
# Index

## Overview
## Concepts
## Entities
## Sources
## Queries
## FAQ
```

* **`## Overview`**：僅簡短導向（範圍、使用方式、指向 repo 根 **`AGENTS.md`** 與 **`wiki/README.md`**）。以數條 bullet 為宜；勿重複完整分類—**Concepts** 起為連結目錄。**維護產物**（如 `wiki/lint/*` 摘要、`wiki/graph/knowledge-map.md`）若需出現在目錄，以 **連結 + 一行說明** bullet 列於此；預設 **無** 獨立 `## Lint`／`## Graph` 章節。
* **`## Concepts` … `## FAQ`**：每條 = **連結 + 一行說明**。

---

# 🛠 操作：Ingest

1. 讀取 **指定** 來源檔（本次 ingest 提供之路徑或 artifact）。
2. **歸檔** 至 `raw/sources/*.md`（僅新檔；檔名依團隊慣例；遵循 **檔案與路徑命名**）。**勿**覆寫或就地修改 `raw/` 既有檔，除非已明確核准。
3. 依 `raw/sources/` 歸檔稿建立或更新 `wiki/sources/`。
4. 抽取：

   * concepts
   * entities
5. 更新相關頁面
6. 建立連結
7. 更新 index
8. Append log

---

# ❓ 操作：Query

1. 讀取 index
2. 找相關頁
3. 綜合回答
4. 引用來源
5. 標記不確定性
6. 若答案可重用，持久化至 `wiki/queries/*` 並更新 `wiki/index.md`（**Queries** 區）。
7. **一律** append `wiki/log.md`（僅回答、未改 wiki 頁時記 **pass**／**no-op**）。

## Query 解析規則（強制）

1. 先查 `wiki/` 摘要頁（`faq`、`concepts`、`entities`、`queries`）。
2. 摘要足夠且無衝突 → 直接回答。
3. 不足、模糊或衝突 → 回到 `raw/sources/*` 核對。
4. 最終答案須含可追溯位置（至少檔案路徑；必要時到章節／行）。

---

# 📚 操作：FAQ

## 目的

自既有 wiki 產出可重用知識

---

## 步驟

1. 讀取 `wiki/index.md`
2. 掃描：

   * sources
   * concepts
   * entities
   * queries
3. 偵測：

   * 重複模式
   * 易混淆主題
   * 工作流程
   * 跨頁關係
4. 產出 FAQ（初階 → 進階）
5. 持久化至 `wiki/faq/`
6. 更新 `wiki/index.md`（FAQ 區：每條 = 連結 + 一行說明）
7. Append `wiki/log.md`

---

## FAQ 頁格式

```yaml
---
title: "<FAQ title>"
type: "query"
status: "active"
updated: "YYYY-MM-DD"
source_count: 0
tags: ["faq"]
---
```

```md
# <FAQ Title>

## Scope

說明範圍

## FAQ

### 1. 問題

**Short Answer：**  

**Detailed Answer：**  

**Related Pages：**
- [[concepts/...]]
- [[sources/...]]
```

---

## FAQ 規則

* 8–15 題
* 須包含：

  * 初學者問題
  * 跨頁綜合題
* 不可虛構無 wiki 依據的題目

---

# 🧪 操作：Lint

偵測：

* 矛盾
* 過時資訊
* 孤兒頁
* 缺頁
* 重複概念
* 無來源頁
* 超過 30 天未更新

輸出 → `wiki/lint/`

**新增或實質變更** `wiki/lint/` 持久化產物時，若目錄需露出，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）（例如 lint 摘要頁）。

**每次** Lint **一律** append `wiki/log.md`（即使未寫新檔 — 記 pass 或簡短摘要）。

---

# 🧠 操作：Graph

建立知識關係：

1. 遍歷所有頁面
2. 抽取連結
3. 推論關係
4. 產出 graph 摘要
5. **新增或實質變更** graph 產物時，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）（例如 `wiki/graph/knowledge-map.md`）
6. Append `wiki/log.md` — **每次** Graph 皆執行，含可選輸出或未變更（記 pass／no-op）

可選輸出：

```md
wiki/graph/knowledge-map.md
```

---

# 🪵 日誌規則

`wiki/log.md` 對應 OKF 選用 [log.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)（§7）。本倉在日期分組之上，以 **操作類型** 留痕（Agent 維護用）。

僅可 append：

```md
## [YYYY-MM-DD] <operation> | <title>
```

（日期標題須為 ISO `YYYY-MM-DD`，與 OKF log 日期標題相容。）

---

# 🚫 硬約束

* **不可**修改 `raw/` **既有**檔（不可變）。Ingest 第二步 **新增** 歸檔至 `raw/sources/` 允許。
* 不可無標記地臆測
* 一律引用
* 一律建立頁面連結
* 完成本文件定義之 **任一** 操作時，**一律** append `wiki/log.md`（每次留痕；允許 pass／no-op）
* 操作 **新增／刪除／實質變更** wiki 頁或目錄所列產物時，更新 `wiki/index.md`；各操作若有更窄規則（例如 Graph：僅 graph 產物變更後才更新 index），**從其規定**

---

# 🧠 行為原則

* 保守 ＞ 發揮
* 明確 ＞ 暗示
* 連結 ＞ 孤立
* 結構 ＞ 冗長

---

# ⚡ Agent 提示詞與 Skill

* **複製貼上提示詞**、**Wiki log append**、**範例指令** → [**docs/PROMPTS.md**](docs/PROMPTS.md)（**步驟單一來源**）
* **總覽 Skill** → [**SKILL.md**](SKILL.md)
* **薄 Skill 觸發**（`/ingest`、`/query`、`/lint`、`/faq`、`/graph`）→ [`.cursor/skills/`](.cursor/skills/)（委派 PROMPTS；規約仍見本檔）
