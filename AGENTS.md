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

# 📁 目錄契約

* `raw/`：既有來源的 **不可變** 區（❗ 不可就地修改）。**Ingest** 第二步可將 **新** 檔 **歸檔** 至 `raw/sources/`。

* `raw/assets/`：選用之圖片／附件，由來源或 wiki 頁引用（不解析為知識頁；Ingest 或維護時視需要新增）。

* `wiki/`：由 LLM 管理的知識庫

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

  * `docs/onboarding.md` — **非 wiki** 之虛構上手流程；含 concept／entity 頁 inline 範例。

  * **Operations Prompts（複製貼上）** — Ingest／Query／Lint／FAQ／Graph 之 Agent 提示詞見本檔下方 **Operations Prompts（複製貼上）**；以此為唯一維護來源。

---

# 🧱 Wiki 頁面約定

* 僅 Markdown

* 除 `wiki/index.md`（總目錄）外，wiki 頁須含 YAML frontmatter（見下方 **必填 Frontmatter**）

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

# 📌 必填 Frontmatter

```yaml
---
title: "<Page title>"
type: "<overview|entity|concept|source|query|lint>"
status: "<draft|active|needs-review>"
updated: "YYYY-MM-DD"
source_count: 0
tags: []
---
```

### `wiki/index.md`（總目錄）

* 本檔 **YAML frontmatter 可省略**。必要結構為 **索引結構** 標題排版（`# Index`、`## Overview`…）；缺 frontmatter 不視為不合規。
* schema 中 `type: "overview"` 供團隊自訂之獨立概覽頁（例如 `wiki/overview.md`）；**非** `wiki/index.md` 必填。
* 若為 `wiki/index.md` 加上 frontmatter，鍵名與 **必填 Frontmatter** 相同（例如 `type: overview`、`title` 描述總目錄）。

---

# 🔗 連結規則（強制）

* 每頁至少連結 ≥1 頁
* 每個新頁須被別處引用
* 盡量雙向連結

### Wiki 連結慣例

* 內文使用 wiki 式連結，不含 `wiki/` 前綴，例如 `[[sources/example]]`、`[[concepts/api]]`、`[[entities/spring-boot]]`。
* 路徑相對於 `wiki/` 解析（檔案為 `wiki/sources/example.md` 等）。
* 自 wiki 頁連至總目錄或支援文件時，`[[../index]]`（即 `wiki/index.md`）以及 repo 根目錄 **`AGENTS.md`**、**`docs/onboarding.md`** 均為有效目標。

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

* 所有可驗證主張須引用來源

格式：

```md
[[sources/ch1]]
```

多個來源：

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
title: "<Page title>"
type: concept
status: draft
updated: "YYYY-MM-DD"
source_count: 1
tags: []
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

`wiki/faq/` 使用下方 **FAQ 頁格式**（非本骨架）。concept／entity 路徑實例見 **`docs/onboarding.md`** 步驟 3。

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

僅可 append：

```md
## [YYYY-MM-DD] <operation> | <title>
```

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

# 📋 Operations Prompts（複製貼上）

Ingest／Query／Lint／FAQ／Graph 之標準提示詞。日誌：本文件定義之 **每次** 操作須 append `wiki/log.md`（無檔案變更時用 **pass** 或 **no-op**）。若操作新增／刪除／實質變更 wiki 頁或目錄所列產物，更新 `wiki/index.md`（各操作另有更細規則，見上文）。

---

## Ingest 提示詞

將本 repository 作為以來源為根據的 wiki 系統。

嚴格遵循本文件（`AGENTS.md`）：
1. 讀取指定來源檔。
2. 歸檔至 `raw/sources/*.md`（僅新檔；勿修改 `raw/` 既有檔）。
3. 依歸檔稿建立或更新 `wiki/sources/*`，區塊標題須符合 **來源頁 Schema**（`Summary`、`Key Concepts`、`Entities`、`Notable Claims`、`Limitations / Gaps`）。版型：`docs/templates/page-template-source.md`。
4. 抽取並更新 `wiki/concepts/*`、`wiki/entities/*`。
5. 視需要建立雙向連結。
6. 更新 `wiki/index.md`。
7. Append `wiki/log.md`。
8. 必要時標記不確定性；所有主張須引用來源。

---

## Query 提示詞

以可追溯、以來源為根據的流程回答使用者問題。

依序：
1. 先查 `wiki/` 摘要頁（`faq`、`concepts`、`entities`、`queries`）。
2. 摘要足夠且無衝突 → 直接回答。
3. 不足、模糊或衝突 → 核對 `raw/sources/*`。
4. 答案須含可追溯位置（至少檔案路徑；必要時章節／行）。
5. 引用來源並標記不確定性（`（確定）`、`（推測）`、`（未知）`）。
6. 若可重用，持久化至 `wiki/queries/*` 並更新 `wiki/index.md`（**Queries** 區：連結 + 一行說明）。
7. **一律** append `wiki/log.md` — 含僅回答、未持久化（記 **pass** 或 **no-op**，見下方 **Wiki log append**）。

---

## Lint 提示詞

執行 wiki 品質 Lint，附證據回報。

遵循上文 **操作：Lint**。

檢查：
- 矛盾
- 過時資訊
- 孤兒頁
- 缺頁
- 重複概念
- 無來源頁
- 過時頁面

結果輸出至 `wiki/lint/`，附可執行修正與檔案級引用。**新增或實質變更** lint 產物時，若目錄需露出，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）。

**一律** append `wiki/log.md`（即使未寫新 lint 檔）：一行摘要，例如 `pass`、`no issues` 或簡短發現。

---

## FAQ 提示詞

自既有 wiki 產出可重用 FAQ。

遵循 **操作：FAQ** 與 **FAQ 頁格式**／**FAQ 規則**。

1. 讀取 `wiki/index.md`。
2. 掃描 sources、concepts、entities、queries。
3. 偵測重複模式、易混淆主題、流程、跨頁關係。
4. 產出 8–15 題（初階至進階，至少一題跨頁綜合）。勿虛構 wiki 無依據的題目。
5. 持久化至 `wiki/faq/`，使用規定 frontmatter（`type: query`、`tags: ["faq"]` 等）及 Scope／FAQ／Short Answer／Detailed Answer／Related Pages 結構。
6. 更新 `wiki/index.md`（FAQ 區：連結 + 一行說明）。
7. Append `wiki/log.md`。

---

## Graph 提示詞

建立或更新本 wiki 知識關係。

遵循 **操作：Graph**。

1. 遍歷 wiki 頁（遵守本文件連結與關係規則）。
2. 抽取連結並適當推論關係。
3. 產出或更新 graph 摘要（可選產物範例：`wiki/graph/knowledge-map.md`）。
4. **新增或實質變更** graph 產物時，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）。
5. **一律** append `wiki/log.md` — 含可選輸出或 **未變更**（記 `pass`、`no-op` 或一行摘要）。

---

## Wiki log append（pass／no-op）

本文件任一操作在 **無須改檔** 但仍須留痕時使用（例如 Lint／Graph 通過且無新產物）。

1. 以 `## [YYYY-MM-DD] <operation> | <title>` 格式 append 新章節至 `wiki/log.md`。
2. 一至兩條 bullet：標 **pass**、**no-op** 或簡述結果；註明操作（lint／graph／faq／ingest／query persist 等）。
3. 勿改寫或刪除既有 log 章節。

---

# ⚡ 範例指令

```md
- Ingest：指定路徑 → 歸檔 raw/sources/*.md → wiki（依 Ingest 步驟；用上方 Ingest 提示詞）
- Ingest raw/sources/ 下既有檔（每檔一輪；更新 index + log）
- 自現有 wiki 產生 FAQ（8–15 題、勿虛構；用 FAQ 提示詞）
- 回答：<問題>（附引用與不確定性標記；用 Query 提示詞）
- Lint wiki（用 Lint 提示詞）
- 建立知識 graph（例如 wiki/graph/knowledge-map.md；用 Graph 提示詞）
```
