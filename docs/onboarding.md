# 部門 Wiki 上手（假資料流程）

本檔為 **支援文件**（不計入 `wiki/` 知識本體），示範同事從空白範例 repo 完成 **第一輪 Ingest** 時，檔案會如何出現。以下路徑與內容皆為 **虛構範例**；請在 **你們部門自己的 repo** 裡依真實來源操作，勿將假資料提交回本範例倉。

規約與 Agent 複製提示：[AGENTS.md](../AGENTS.md)（**Operations Prompts（複製貼上）**）

---

## 採用前：建立部門專用 repo

1. 以本倉 **GitHub Template** 或 **fork** 建立新 repo（例如 `llm-wiki-部門名稱`）。
2. **不要**在共用的 `llm-wiki-example` 上直接寫各部門知識。
3. 編輯 `wiki/index.md` 的 **Overview**：部門名稱、知識範圍、維護者。

---

## 假設情境

部門收到一份內部說明稿《訂單 API 簡介》（虛構），要納入 wiki。

---

## 步驟 1：歸檔來源（`raw/sources/`）

**新增**（不可覆寫既有檔）：

`raw/sources/訂單-api-簡介.md`

```markdown
# 訂單 API 簡介（虛構來源稿）

訂單服務提供 REST API。建立訂單使用 POST /orders。
回應含 order_id。詳見訂單服務文件 v2。
```

命名：依 **AGENTS.md** 使用繁體字面或英文識別名，**勿**用漢語拼音（例如避免 `dingdan-api.md`）。

---

## 步驟 2：建立來源頁（`wiki/sources/`）

`wiki/sources/訂單-api-簡介.md`（版型：[page-template-source.md](./templates/page-template-source.md)）

```yaml
---
title: "訂單 API 簡介"
type: source
status: active
updated: "2026-06-17"
source_count: 1
tags: ["api", "訂單"]
---
```

必填區塊：`Summary`、`Key Concepts`、`Entities`、`Notable Claims`、`Limitations / Gaps`。  
內文引用歸檔稿：`[[sources/訂單-api-簡介]]` 或標註 `raw/sources/訂單-api-簡介.md`。  
至少連結一頁，例如概念頁 `[[concepts/rest-api]]` 或目錄 `[[../index]]`。

---

## 步驟 3：抽取概念與實體

| 類型 | 建議路徑 | 說明 |
|------|----------|------|
| 概念 | `wiki/concepts/rest-api.md` | 抽象：REST API 原則 |
| 實體 | `wiki/entities/訂單服務.md` | 具體：部門內的訂單服務系統 |

兩頁皆需 frontmatter、`source_count`、引用 `[[sources/訂單-api-簡介]]`，並與來源頁 **雙向連結**。區塊名稱為建議用語（詳 **AGENTS.md** → **Concept / Entity / Query / Lint Pages**），例如概念頁：

```yaml
---
title: "REST API"
type: concept
status: active
updated: "2026-06-17"
source_count: 1
tags: ["api"]
---
```

```markdown
# REST API

## Summary

部門內以 HTTP 動詞與資源路徑表達操作的 API 風格。（確定）[[sources/訂單-api-簡介]]

## Key Points

- 建立資源常用 POST。（確定）[[sources/訂單-api-簡介]]

## Evidence

- 訂單 API 簡介提及 POST /orders。[[sources/訂單-api-簡介]]

## Relationships

- related_to: [[entities/訂單服務]]
- used_in: [[sources/訂單-api-簡介]]
```

---

## 步驟 4：更新總目錄（`wiki/index.md`）

在對應章節新增 **連結 + 一行說明**，例如：

```markdown
## Concepts

- [REST API](./concepts/rest-api.md) — 部門內 REST 風格 API 的共通約定。

## Entities

- [訂單服務](./entities/訂單服務.md) — 提供訂單 CRUD 的後端服務。

## Sources

- [訂單 API 簡介](./sources/訂單-api-簡介.md) — 虛構內部稿之收斂摘要。
```

Lint／Graph 產物若需出現在目錄，加在 **Overview** 區塊（本契約無獨立 `## Lint` / `## Graph` 章節）。

---

## 步驟 5：append 操作日誌（`wiki/log.md`）

```markdown
## [2026-06-17] ingest | 訂單 API 簡介（虛構範例）

- 歸檔 `raw/sources/訂單-api-簡介.md`；新增 `wiki/sources/訂單-api-簡介.md`、`wiki/concepts/rest-api.md`、`wiki/entities/訂單服務.md`。
- 更新 `wiki/index.md` Concepts / Entities / Sources。
```

---

## 步驟 6（可選）：Query 與 FAQ

| 需求 | 位置 | 說明 |
|------|------|------|
| 單一可重用問答 | `wiki/queries/` | 例如「如何建立訂單？」一題一頁 |
| 題組（8–15 題） | `wiki/faq/` | frontmatter `type: query` 且 `tags: ["faq"]` |

兩者不同：`queries` 是單題持久化；`faq` 是結構化題組頁。

Query 僅回答、不寫入 wiki 時，仍須 **append `wiki/log.md`**（`pass` / `no-op`）。

---

## 給 Agent 的一句話

> 依 AGENTS.md Ingest 指定路徑 `<path>`：歸檔至 `raw/sources/`、更新 `wiki/sources`、抽取 concepts／entities、更新 `wiki/index.md`、append `wiki/log.md`。使用 AGENTS.md **Operations Prompts（複製貼上）** 中的 **Ingest 提示詞**。

---

## 檢查清單（第一輪完成後）

- [ ] `raw/sources/` 有新歸檔，且未就地改寫舊檔
- [ ] 每個新 wiki 頁有 frontmatter 與 ≥1 連結
- [ ] 可驗證敘述有 `[[sources/...]]` 或 `raw/` 路徑
- [ ] `wiki/index.md` 已列出所有新頁
- [ ] `wiki/log.md` 已 append 本輪操作
