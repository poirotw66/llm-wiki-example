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

本倉以 **[Open Knowledge Format（OKF）v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)** 為知識表示主軸（參考 [knowledge-catalog/okf](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)）。`wiki/` 即 **Knowledge Bundle**；其餘目錄與操作規則為在 OKF 之上的 **本倉擴充**（可追溯歸檔、Agent 維護流程）。

| OKF 術語 | 本倉對應 |
|----------|----------|
| Knowledge Bundle | `wiki/` |
| Concept | `wiki/**/*.md`（保留檔名 `index.md`、`log.md`、`purpose.md`、`queue.md`、`insights.md`、`README.md` 除外） |
| Concept ID | 相對 `wiki/` 之路徑去掉 `.md`（例：`concepts/rest-api`、`entities/my-service`） |
| `index.md` | `wiki/index.md`（漸進式揭露總目錄） |
| `log.md` | `wiki/log.md`（變更歷史；本倉另訂操作日誌格式） |

**OKF 合規（v0.2）**：每個 Concept 須有可解析 YAML frontmatter，且含非空 `type`。其餘約束見下方 Frontmatter 與 [**docs/okf.md**](docs/okf.md)。

**本倉擴充（不違反 OKF 消費端容忍未知鍵）**：`raw/` 不可變歸檔、企業資料治理欄位、來源頁 Schema、五大操作與 `wiki/log.md` 操作留痕。`status`、`sources`、`generated`、`verified` 與 `stale_after` 為 OKF v0.2 欄位，不是本倉私有欄位。

---

# 📁 目錄契約

* `raw/`：既有來源的 **不可變** 區（❗ 不可就地修改）。Ingest 依 [**docs/ingest-pipeline.md**](docs/ingest-pipeline.md) 寫入新檔。來源修訂時 **另建新歸檔檔**（勿改寫既有 `raw/` 檔）；slug 慣例見 [**docs/okf.md**](docs/okf.md) → **`archive_slug` 與 resource**。

* `raw/inbox/`：使用者提供、**待處理** 之原件（PDF、Office、圖片、MD 等）；Ingest 可從此讀取。**成功歸檔後刪除** inbox／repo 根目錄等輸入副本（見 **操作：Ingest** 步驟 15）。

* `raw/originals/`：**所有輸入原件**之不可變副本（**含 Markdown**、PDF、Office、圖片等；新檔歸檔；勿改寫既有檔）。保留原始檔名與位元內容（或與輸入一致之副檔名）。

* `raw/sources/`：**canonical Markdown** 歸檔稿（**盡可能詳盡還原**，非 wiki 級精簡；可由原件轉寫、清理或補強）；`wiki/sources/` 為摘要頁，以本倉 `archive_slug` 對應歸檔檔名，並以 OKF `sources[].resource` 引用歸檔稿。

* `raw/assets/`：自視覺萃取之圖片／附件；**依 `<base-slug>` 分子目錄**（`raw/assets/<base-slug>/p<NN>.png`，見 **docs/pdf-ingest-sop.md**）；由歸檔稿或 wiki 頁引用（不解析為知識頁）。

* `wiki/`：**OKF Knowledge Bundle**（由 LLM／人類維護的知識本體）

* `wiki/index.md`：總目錄（canonical catalog）

* `wiki/purpose.md`：wiki **方向**（目標、關鍵問題、範圍）；與 AGENTS／PROMPTS 的操作 schema 分離

* `wiki/review/queue.md`：非同步人審佇列（Ingest 可 append，不阻擋寫入）

* `wiki/log.md`：僅可 append 的操作日誌

* `wiki/sources/`：自來源整理之知識頁

* `wiki/concepts/`：抽象概念（MVC、API、Transaction）

* `wiki/entities/`：具體系統（Vue、Spring Boot、JDBC）

* `wiki/queries/`：可重用之 **單一** 問答頁（一題 → 一則持久化答案）

* `wiki/faq/`：結構化 **FAQ 題組**（每頁 8–15 題；frontmatter `type: query` 且 `tags: ["faq"]` — `type` 表示頁面形狀，非 `wiki/queries/` 資料夾）

* `wiki/lint/`：診斷／檢查結果

* `wiki/graph/`：關係對照（選用、進階）

* `docs/`（**支援文件**，不計入 wiki 知識本體）：

  * `docs/templates/ingest-analysis.md` — **兩段式 Ingest** 分析稿骨架（寫入 `.llm-wiki/ingest/analyses/`）。

  * `docs/templates/page-template-source.md` — 僅供 **`wiki/sources/*`** 起稿；區塊標題須與下方 **來源頁 Schema** 完全一致。

  * `docs/templates/page-template-concept.md` — 供 **`wiki/concepts/*`**、**`wiki/entities/*`**、**`wiki/queries/*`** 起稿（建議骨架）。

  * `docs/ingest-pipeline.md` — **Ingest 管線對照**（完整步驟以 PROMPTS／AGENTS 為準；含快取／兩段式／Review）。

  * `docs/visual-source-conversion.md` — 含資訊性視覺時之轉換與 Visual Evidence Block。

  * `docs/pdf-ingest-sop.md` — **PDF 轉譯 SOP** 與 **`<base-slug>`／資產命名**（`-p<NN>.png`）。

  * `docs/onboarding.md` — 第一輪 Ingest 解說；對照 **docs/templates/** 版型。

  * `docs/PROMPTS.md` — **Operations Prompts（複製貼上）** 與範例指令；Agent **操作步驟**之唯一維護來源。

  * `docs/okf.md` — **OKF v0.2 對照、治理與互通**（bundle 映射、欄位、連結、匯出）；規格原文見 [SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)。

  * `docs/data-governance.md` — **企業資料治理與 Git 准入**（分類、owner、PII、保存、遮罩、人工核可與例外）。

  * `SKILL.md`（repo 根）— 總覽 Skill；指向子 Skill 與三步流程。

  * `skills/llm-wiki-{ingest,query,lint,faq,graph}/` — **薄 Skill**（觸發 `/ingest` 等；**Git 單一來源**）；委派 `docs/PROMPTS.md` 對應章節，勿複製長步驟。本機 Cursor 副本可放 `.cursor/skills/`（已 gitignore，見 [README](README.md#cursor-skill-用法)／`npx skills add`）。

### 目錄設計：型別式子目錄（OKF 相容）

OKF **不**規定固定分類法；子目錄僅為組織 Concept 之用（[SPEC §3](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)）。本倉採 **`sources`／`concepts`／`entities`** 等 **知識角色** 分層，而非 `wiki/<topic>/` 純主題目錄——以利 Ingest 落點、Schema 檢查與 Agent 操作。規模變大時可在型別下加領域子目錄（例如 `wiki/entities/billing/invoice-service.md`），無須改為純主題式。

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

### OKF v0.2（規格層）

| 層級 | 鍵 | 說明 |
|------|-----|------|
| **必填** | `type` | 概念種類；本倉慣用 `concept`、`entity`、`source`、`query`、`lint`（亦符合 OKF「自描述型別字串」） |
| **建議** | `title` | 顯示名稱 |
| **建議** | `description` | 一語摘要（index、搜尋預覽） |
| **建議** | `resource` | 底層資產的 URI（HTTPS、bundle-relative 或相對路徑）；見 **`docs/okf.md`** → **resource 語意** |
| **建議** | `tags` | 標籤列表 |
| **建議** | `sources` | 來源清單；每項須有 `resource`，主張以同項 `id` 的 footnote 對應 |
| **建議** | `generated` | `{ by: <actor>, at: <ISO 8601> }`；記錄目前內容的產生者與最後有意義變更時間 |
| **建議** | `verified` | 驗證事件（mapping 或 list）；`human:<id>` 代表人審 |
| **建議** | `status` | `draft` \| `stable` \| `deprecated`；缺省為 `stable` |
| **建議** | `stale_after` | `YYYY-MM-DD`；當日及之後視為 stale |

規格與範例見 [OKF SPEC §4–5](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)。

### 本倉擴充（資料治理層）

| 鍵 | 說明 |
|-----|------|
| `classification` | `public` \| `internal` \| `confidential` \| `restricted` |
| `owner` | `team:<id>`、`human:<id>` 或 `process:<id>` |
| `access_scope` | `public` \| `organization` \| `team:<id>` \| `named:<approved-group>` |
| `contains_pii` | `true` \| `false` \| `unknown` |
| `retention` | `permanent` \| `until:<YYYY-MM-DD>` \| `per-policy:<id>` |
| `redaction` | `none` \| `applied` \| `required` |

```yaml
---
type: concept
title: "<Page title>"
description: "<一語摘要>"
resource: "<URI；抽象 concept 可省略>"
tags: []
sources:
  - id: "<stable-source-id>"
    resource: "<URL、bundle-relative 或相對路徑>"
    title: "<來源標題>"
generated: { by: "<agent/version|human:id|process:id>", at: "YYYY-MM-DDTHH:MM:SSZ" }
status: draft
stale_after: "YYYY-MM-DD"
classification: internal
owner: "team:<id>"
access_scope: "team:<id>"
contains_pii: unknown
retention: "per-policy:<id>"
redaction: required
---
```

互通對照與匯出映射見 **`docs/okf.md`**。

本範例僅接受 OKF v0.2 語法；lint 會拒絕非 v0.2 lifecycle、舊 metadata、bare `resource` slug 與非 keyed provenance。人審規則見 [docs/okf.md](docs/okf.md) 與 [docs/data-governance.md](docs/data-governance.md)。

### `wiki/index.md`（bundle 根 index）

* 本範例在 bundle 根 `index.md` **必須**加 `okf_version: "0.2"`，且 frontmatter 僅可含此鍵（[§12](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)）。
* 必要結構為下方 **索引結構** 標題排版（`# Index`、`## Overview`…）。
* schema 中 `type: "overview"` 供團隊自訂之獨立概覽頁（例如 `wiki/overview.md`）；**非** `wiki/index.md` 必填。

---

# 🔗 連結規則（強制）

* 每頁至少連結 ≥1 頁（OKF 跨頁關係；見 [SPEC §6](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)）
* 每個新頁須被別處引用
* 盡量雙向連結

### Bundle 內連結（強制格式）

`wiki/` **嵌於本 repo** 時，GitHub／IDE **無法** 解析 OKF 的 `/concepts/foo.md`（會指向網站或磁碟根目錄而斷鏈）。Concept 互連 **一律** 使用 **markdown 相對路徑**（含 `.md`）：

```md
<!-- 自 wiki/concepts/my-concept.md -->
見 [API 簡介](../sources/my-api-intro.md)。

<!-- 自 wiki/sources/my-api-intro.md -->
見 [REST 約定](../concepts/my-concept.md)。
```

| 起點 | 連至同層鄰居 | 連至其他型別子目錄 |
|------|--------------|-------------------|
| `wiki/concepts/` | `./other.md` | `../sources/foo.md`、`../entities/bar.md` |
| `wiki/sources/` | `./本頁.md` | `../concepts/foo.md` |
| `wiki/index.md` | — | `./concepts/foo.md` |

**OKF `/path.md`**：僅用於 **獨立 bundle 匯出**（`wiki/` 為根目錄）或 OKF visualize 等消費端；撰寫時勿用。

**禁止** `[[concepts/...]]` wiki 式連結。

連至 [Index](../index.md)（自子目錄）或 `./index.md`（自 `wiki/index.md`）。連至 `wiki/` 外支援文件：`../../AGENTS.md`、`../../docs/PROMPTS.md` 等（依深度調整 `../`）。

### 冷啟動（空白 wiki）

* 第一則知識頁建立前，骨架無 wiki 頁可互連。**第一次 Ingest 後**，每個新頁至少連結一個其他 wiki 頁（通常連至 `../index.md`，或 source／concept／entity 頁互連）。

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

- related_to: [API](../concepts/api.md)
- implemented_by: [Spring Boot](../entities/spring-boot.md)
- used_in: [ch1](../sources/ch1.md)
```

👉 供日後 graph 推理（RAG／agents）

---

# 📏 頁面粒度規則

* 一頁 = 一概念或一實體
* 超過 500 字 → 拆分
* 不可混用不同抽象層次

---

# 📌 來源與引用規則（關鍵）

* 所有可驗證主張須引用 frontmatter `sources`（OKF [§5.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)）。每個 `sources[]` 項目須有 `resource`；欲逐一歸因的項目必有穩定 `id`，並用 `[^<id>]` footnote 連結。

**Bundle 內來源 Concept**（路徑相對於**當前檔案**）：

```md
[來源標題](../sources/ch1.md)
```

**外部 URL 或歸檔稿**：先在 frontmatter 宣告，再在內文以 footnote 歸因，例如：

```md
來源內容的主張。[^official-doc]

[^official-doc]: 官方文件
```

```yaml
sources:
  - id: official-doc
    resource: https://example.com/docs
    title: 官方文件
```

**歸檔稿**（`raw/sources/*`）應以 `sources[].resource` 的相對路徑或核准外部識別記錄，例如 `../../raw/sources/ch1.md`（自 `wiki/sources/`）；主張一律使用與 `sources[].id` 相同的 keyed footnote。

多個 bundle 內來源：

```md
[ch1](../sources/ch1.md)、[ch3](../sources/ch3.md)
```

---

# ⚠️ 不確定性標記

有根據的主張**不需標記**；僅在以下情況加標記：

* （推測）— 有合理依據但未直接確認
* （未知）— 無法從現有來源判斷

---

# 📚 來源頁 Schema

每個 `wiki/sources/*` 須包含：

```md
## Summary
- 3–5 bullets

## Key Concepts

## Entities

## Notable Claims

## Visual Assets

> 來源含資訊性視覺時必填；無則省略。須 `![]()` embed `../../raw/assets/<base-slug>/p<NN>.png`（見 **visual-source-conversion.md**、**pdf-ingest-sop.md**）。

## Limitations / Gaps
```

來源頁起稿版型：**`docs/templates/page-template-source.md`**。概念／實體／Query 起稿：**`docs/templates/page-template-concept.md`**。

---

# 📄 Concept／Entity／Query／Lint 頁（建議骨架）

**`wiki/concepts/*`**、**`wiki/entities/*`**、**`wiki/queries/*`**、**`wiki/lint/*`**：使用 **Frontmatter（OKF + 本倉擴充）**；下列區塊名稱為 **建議**（不如 **來源頁 Schema** 嚴格）。`type` 設為 `concept` | `entity` | `query` | `lint`。有根據的主張須引用來源。起稿見 **`docs/templates/page-template-concept.md`**。

```yaml
---
type: concept
title: "<Page title>"
description: "<一語摘要>"
resource: "<URI；抽象 concept 可省略>"
tags: []
sources:
  - id: "<stable-source-id>"
    resource: "<URL、bundle-relative 或相對路徑>"
    title: "<來源標題>"
generated: { by: "<agent/version|human:id|process:id>", at: "YYYY-MM-DDTHH:MM:SSZ" }
status: draft
classification: internal
owner: "team:<id>"
access_scope: "team:<id>"
contains_pii: unknown
retention: "per-policy:<id>"
redaction: required
---
```

```md
# <Page title>

## Summary

一段概述。

## Key Points

- 要點並引用 [來源](../sources/....md)

## Evidence

- 有根據的主張 → [來源](../sources/....md) 或 `../../raw/sources/<slug>.md`

## Relationships

- related_to: [概念](../concepts/....md)
- implemented_by: [實體](../entities/....md)

## Open Questions

- 待釐清事項（選填）
```

`wiki/faq/` 使用下方 **FAQ 頁格式**（非本骨架）。版型與流程見 **`docs/templates/page-template-concept.md`**、**`docs/onboarding.md`**。

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

---

# 🗂 來源轉換政策（階段 1）

每次 Ingest **必須** 以 **detect／triage** 開頭（借鑑 Graphify 分流；落地為 BU + OKF 管線，詳見 [**docs/ingest-pipeline.md**](docs/ingest-pipeline.md)）。

## 轉換規則

* **先資料治理，後落盤**：在複製至 workspace、`raw/` 或 Git 前，依 [docs/data-governance.md](docs/data-governance.md) 判定 `classification`、`owner`、`access_scope`、PII、retention 與 redaction。`confidential`／`restricted`、`contains_pii: true|unknown`、`redaction: required` 或疑似秘密時，停止自動 Ingest，待 owner／資料治理人工核可；不可因 `raw/` 不可變而繞過 Git 准入。
* **一律**先將輸入原件複製至 `raw/originals/`（**含 Markdown**）。
* 非 Markdown 或含不可讀視覺之來源 → 轉 **結構化 Markdown** 後寫入 `raw/sources/`（**詳盡還原稿**，見 **docs/visual-source-conversion.md**）；純 MD 輸入亦須另寫 canonical 至 `raw/sources/`（可清理／補強，不可省略 originals）。
* 支援類型：`.md`、`.txt`、`.docx`、`.pdf`、`.ppt`/`.pptx`、`.xlsx`、常見圖片格式（見 ingest-pipeline 表）。
* 含流程圖、架構圖、截圖、ER、掃描頁等 → 依 [**docs/visual-source-conversion.md**](docs/visual-source-conversion.md)；資產入 `raw/assets/`。**PDF** 預設 **fast**：`pdftotext` + 頁級分流（`scripts/docling-pdf.py`，`--engine fast`）→ 文字頁直入；**僅**資訊圖／文字層極短頁再 `pdftoppm` + vision／VLM（見 [**docs/pdf-ingest-sop.md**](docs/pdf-ingest-sop.md)）。**僅使用者明確指定** full／Docling 時才用 `--engine docling`；Agent 不得自行升級。[Docling](https://github.com/docling-project/docling) 為可選路徑。**文字層極短但頁面有架構圖時，必須 vision 寫層／節點盤點，禁止只抄標題。** Visual Evidence **就地**寫在該頁／該節下，**禁止**文末彙整所有圖。**讀圖一律 subagent**（見 visual-source-conversion → 平行 Vision 編排）；主 Agent **禁止**自行讀圖。
* 無資訊性視覺 → log 或歸檔稿註明「視覺轉換閘：未適用」。
* 視覺無法辨識 → 保留資產（若可）、標 `（未知）`、寫入 **Limitations / Gaps**。
* 資產路徑為 **`raw/assets/<base-slug>/p<NN>.png`**（見 **docs/pdf-ingest-sop.md**）；頁碼須與「來源位置」一致；修訂歸檔時 **另建新檔**（如 `YYYYMMDD_<base-slug>.md`），勿改寫既有 `raw/sources/`。

## 歸檔檔名（`<archive-slug>`）

* 全檔：`<base-slug>.md`（與 `resource` 一致）。
* 部分頁：`<base-slug>-頁<start>至<end>.md`（例：`…-頁1至5.md`）。
* 修訂版：`YYYYMMDD_<archive-slug>.md`；**勿**改寫既有 `raw/sources/` 檔。

---

# 🛠 操作：Ingest

下列為 Ingest 業務步驟（對照 [**docs/ingest-pipeline.md**](docs/ingest-pipeline.md)）。開始前讀 [**wiki/purpose.md**](wiki/purpose.md)。Token telemetry：`start ingest`／`finish ingest`（同 title）。

1. 讀取 **指定** 來源（路徑、`raw/inbox/` 或批次）。
2. **SHA-256 快取**：`python3 scripts/ingest-cache.py lookup "<path>"`。若 `hit: true` 且使用者未要求強制重跑 → append log **no-op**（註明 sha256／既有 archive_slug）並結束。
3. **Detect／Triage**（檔型、是否需轉檔、是否含資訊性視覺）。
4. 必要時 **轉 Markdown**（含視覺閘；**讀圖一律 subagent**；PDF 預設 **fast**，見 **docs/pdf-ingest-sop.md**）。
5. **一律** 將輸入原件複製至 **`raw/originals/`**（含 `.md`；新檔；勿改寫既有檔）。
6. 視覺資產寫入 **`raw/assets/`**（若適用）。
7. **新增** canonical 歸檔 **`raw/sources/<archive-slug>.md`**（僅新檔；詳盡還原）。
8. **兩段式 · 分析（強制）**：依 [**docs/templates/ingest-analysis.md**](docs/templates/ingest-analysis.md) 寫入 `.llm-wiki/ingest/analyses/<archive-slug>.md`（實體／概念／既有連結／矛盾與張力／建議落點／review candidates）。**禁止**跳過分析直接寫 wiki 頁。
9. **保證來源摘要頁**：建立或更新 **`wiki/sources/<archive-slug>.md`**（來源頁 Schema）。lint 要求每個 `raw/sources/*.md` 有對應 wiki 來源頁。
10. 依分析抽取／更新 **concepts**、**entities**。
11. 更新相關頁並 **雙向連結**（相對路徑）。
12. 補齊 **OKF v0.2 frontmatter** 與治理欄位；來源頁填 `archive_slug`；不可把 agent 自評寫成 `human:` 驗證。
13. 更新 **`wiki/index.md`**；必要時更新 **`wiki/purpose.md`** 的 Evolving thesis（僅在有根據時）。
14. **非同步 Review**：對 review candidates／未答 Q&A／需人審治理項，執行 `python3 scripts/ingest-review.py append ...` 寫入 `wiki/review/queue.md`（**不**阻擋本輪寫入）。
15. **輸入原件清理**（`scripts/ingest-cleanup.py`；先 dry-run 再 `--confirm`）。
16. **Append** `wiki/log.md`；成功後 `python3 scripts/ingest-cache.py record "<path>" --archive-slug … --source-page wiki/sources/….md`。

---

# ❓ 操作：Query

1. 讀取 index
2. 找相關頁
3. 綜合回答
4. 引用來源
5. 標記不確定性
6. 若答案可重用，持久化至 `wiki/queries/*` 並更新 `wiki/index.md`（**Queries** 區）。
7. **一律** append `wiki/log.md`（僅回答、未改 wiki 頁時記 **pass**／**no-op**）。

操作開始前／append log 後，分別以相同 title 執行 `python3 scripts/wiki-usage.py start query --title "<title>"`／`python3 scripts/wiki-usage.py finish query --title "<title>"`；量測欄位僅可記錄 runtime 實際提供的數字。

## Query 解析規則（強制）

**預設模式**（綜合 wiki + 必要時 raw）：

1. 先讀 [**wiki/purpose.md**](wiki/purpose.md) 對齊範圍；再查 `wiki/` 摘要頁（`faq`、`concepts`、`entities`、`queries`）。
2. 摘要足夠且無衝突 → 直接回答。
3. 不足、模糊或衝突 → 回到 `raw/sources/*` 核對。
4. 最終答案須含可追溯位置（至少檔案路徑；必要時到章節／行）。
5. 若答案涉及架構圖、流程圖等資訊性視覺，**必須**附上 `raw/assets/` 原圖的 Markdown embed 或連至含 **`## Visual Assets`** 的來源頁；**禁止**僅文字描述而不給原圖（見 **visual-source-conversion.md** → **可檢索原圖**）。若須重新讀圖分析內容，**一律派 subagent**（主 Agent 禁止自行讀圖）。

**Read Sources Only 模式**（使用者說「僅讀歸檔」「read sources only」「--sources-only」）：

1. **禁止**以 `wiki/concepts|entities|faq|queries` 摘要作為證據來源。
2. 只讀 `raw/sources/*`（必要時 `raw/assets/` 與對應 Visual Evidence）。
3. 答案須標明 `mode: read-sources-only`，並引用歸檔路徑。
4. 仍可將可重用答案持久化至 `wiki/queries/*`（標明證據僅來自 raw）。

---

# 📚 操作：FAQ

## 目的

自既有 wiki 產出可重用知識

---

## 步驟

**空 wiki**：若尚無可掃描的 Concept 頁，勿虛構題目、勿寫入 `wiki/faq/`；append `wiki/log.md` 記 **no-op**（詳見 [**docs/PROMPTS.md**](docs/PROMPTS.md) → FAQ 提示詞）。

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

操作開始前／append log 後，分別以相同 title 執行 `python3 scripts/wiki-usage.py start faq --title "<title>"`／`python3 scripts/wiki-usage.py finish faq --title "<title>"`。

---

## FAQ 頁格式

```yaml
---
title: "<FAQ title>"
type: "query"
sources:
  - id: "<source-page>"
    resource: "../sources/<source-page>.md"
    title: "<來源標題>"
status: stable
generated: { by: "<agent/version|human:id|process:id>", at: "YYYY-MM-DDTHH:MM:SSZ" }
classification: internal
owner: "team:<id>"
access_scope: "team:<id>"
contains_pii: false
retention: "per-policy:<id>"
redaction: none
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
- [概念](../concepts/....md)
- [來源](../sources/....md)

[^<source-page>]: <來源標題>
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

**自動檢查（優先）**：執行 `uv run --group test python3 scripts/wiki-lint.py`（真正 YAML/schema、斷鏈、catalog／孤兒頁、`resource` ↔ `raw/sources/`、生命週期、治理欄位、視覺資產；CI 另以 `--base` 檢查 raw immutability 與 log append-only）。exit code 非 0 時依輸出修正後再跑 Agent 深度 Lint。

偵測：

* 矛盾
* 過時資訊
* 孤兒頁
* 缺頁
* 重複概念
* 無來源頁
* 超過 30 天未更新
* **斷鏈**（`/path.md` 目標不存在於 `wiki/`）
* **`/path.md` 根路徑連結**（在嵌於 repo 的 `wiki/` 內會斷鏈；應改相對路徑）
* **視覺資產缺口**：`raw/assets/` 有對應資產，但 `wiki/sources/*` 缺 **`## Visual Assets`**、缺 `![]()` embed，或 embed 路徑與 `raw/assets/<base-slug>/p<NN>.png` 不一致
* **文末彙整 Visual Evidence**：canonical 歸檔把全部資產 embed 堆在單一 `## Visual Evidence`（應就地放置；見 **docs/visual-source-conversion.md**）

輸出 → `wiki/lint/`

**新增或實質變更** `wiki/lint/` 持久化產物時，若目錄需露出，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）（例如 lint 摘要頁）。

**每次** Lint **一律** append `wiki/log.md`（即使未寫新檔 — 記 pass 或簡短摘要），並在開始／結束以相同 log title 執行 `python3 scripts/wiki-usage.py start lint --title "<title>"`／`python3 scripts/wiki-usage.py finish lint --title "<title>"`；詳見 [docs/skill-usage.md](docs/skill-usage.md)。

---

# 🧠 操作：Graph

建立知識關係。

**空 wiki**：若尚無 Concept 頁可遍歷，勿產出 `wiki/graph/*`；append `wiki/log.md` 記 **no-op**（詳見 [**docs/PROMPTS.md**](docs/PROMPTS.md) → Graph 提示詞）。

1. 遍歷所有頁面
2. 抽取連結
3. 推論關係；並執行 `python3 scripts/wiki-graph-insights.py` 產出／更新 `wiki/graph/insights.md`（孤立頁、橋接、缺來源摘要頁、單向連結）
4. Agent 依 insights 的 **Agent follow-up** 補充矛盾／缺頁判斷（結構腳本不自動判定語意矛盾）
5. 產出或更新 graph 摘要（可選：`wiki/graph/knowledge-map.md`）
6. **新增或實質變更** graph 產物時，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）
7. Append `wiki/log.md` — **每次** Graph 皆執行，含可選輸出或未變更（記 pass／no-op）

操作開始前／append log 後，分別以相同 title 執行 `python3 scripts/wiki-usage.py start graph --title "<title>"`／`python3 scripts/wiki-usage.py finish graph --title "<title>"`。

可選輸出：

```md
wiki/graph/knowledge-map.md
wiki/graph/insights.md
```

---

# 🪵 日誌規則

`wiki/log.md` 對應 OKF 選用 [log.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)（§9）。本倉在日期分組之上，以 **操作類型** 留痕（Agent 維護用）。

僅可 append。新紀錄依 OKF v0.2 使用日期分組；同日多次操作各加一個頂層 bullet，細節使用縮排 bullet：

```md
## YYYY-MM-DD

- **<operation>** | <title>
  - <摘要或 pass／no-op>
```

日期標題須為 ISO `YYYY-MM-DD`；其他 heading 形式不合規。

`.llm-wiki/usage/events.jsonl` 保存 runtime token telemetry。每次操作的 Agent 須在開始／結束以相同 log title 自動執行 `python3 scripts/wiki-usage.py start <operation> --title "<title>"`／`python3 scripts/wiki-usage.py finish <operation> --title "<title>"`；該 ledger 不取代 `wiki/log.md`。詳見 [docs/skill-usage.md](docs/skill-usage.md)。

---

# 🚫 硬約束

* **不可**修改 `raw/` **既有**檔（不可變）。Ingest 第二步 **新增** 歸檔至 `raw/sources/` 允許。
* 不可無標記地臆測
* 一律引用
* 一律建立頁面連結
* 完成本文件定義之 **任一** 操作時，**一律** append `wiki/log.md`，並以相同 title 自動執行 `start <operation> --title "<title>"`／`finish <operation> --title "<title>"` 寫入實測 token ledger（每次留痕；允許 pass／no-op）
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
* **薄 Skill**（`/ingest`、`/query`、`/lint`、`/faq`、`/graph`）→ [`skills/`](skills/)（委派 PROMPTS；規約仍見本檔）。Cursor 請以 `npx skills add` 安裝；`.cursor/` 不進 Git。
