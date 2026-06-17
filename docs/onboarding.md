# 部門 Wiki 上手（Ingest 流程）

本檔說明 **第一輪 Ingest** 步驟。本 **範例 repo** 已將虛構「訂單 API」實作於 `raw/sources/` 與 `wiki/`（見 [`wiki/index.md`](../wiki/index.md)）；部門 **fork 後請刪除或覆寫** 示範內容，改以真實來源操作。

- 規約：[AGENTS.md](../AGENTS.md)（**OKF 主軸**）
- OKF 對照：[docs/okf.md](./okf.md)
- Agent 提示詞：[docs/PROMPTS.md](./PROMPTS.md)
- Skill 入口：[SKILL.md](../SKILL.md)

---

## 採用前：建立部門專用 repo

1. 以 **GitHub Template** 或 **fork** 建立新 repo。
2. **不要**在共用的 `llm-wiki-example` 上寫各部門知識。
3. 編輯 `wiki/index.md` 的 **Overview**；移除 `tags` 含 `範例` 的頁面與示範歸檔稿。

---

## 假設情境

部門收到內部說明稿《訂單 API 簡介》（虛構），要納入 wiki。

---

## 步驟 1：歸檔來源（`raw/sources/`）

**新增** `raw/sources/訂單-api-簡介.md`（本倉已有示範檔）。日後修訂來源時 **另建新歸檔檔**，勿改寫既有 `raw/` 檔。fork 後請改為你們的真實來源。

命名：依 **AGENTS.md** 使用繁體字面或英文識別名，**勿**用漢語拼音。

---

## 步驟 2：建立來源頁（`wiki/sources/`）

見本倉 [`wiki/sources/訂單-api-簡介.md`](../wiki/sources/訂單-api-簡介.md)；版型：[page-template-source.md](./templates/page-template-source.md)。

---

## 步驟 3：抽取概念與實體

| 類型 | 本倉示範路徑 |
|------|----------------|
| 概念 | [`wiki/concepts/rest-api.md`](../wiki/concepts/rest-api.md) |
| 實體 | [`wiki/entities/訂單服務.md`](../wiki/entities/訂單服務.md) |

區塊骨架見 **AGENTS.md** → **Concept／Entity／Query／Lint 頁**。

---

## 步驟 4：更新總目錄（`wiki/index.md`）

各區 **連結 + 一行說明**。本倉示範見 [`wiki/index.md`](../wiki/index.md)。

---

## 步驟 5：append 操作日誌（`wiki/log.md`）

本倉 `wiki/log.md` **刻意留白**（範例 repo 不記維護 log）。部門 fork 後自第一次真實操作起 append。

---

## 步驟 6（可選）：Query 與 FAQ

| 需求 | 本倉示範 |
|------|----------|
| 單一可重用問答 | [`wiki/queries/如何建立訂單.md`](../wiki/queries/如何建立訂單.md) |
| 題組（8 題） | [`wiki/faq/訂單-api-範例-faq.md`](../wiki/faq/訂單-api-範例-faq.md) |

版型：`page-template-concept.md`（`type: query`；FAQ 另加 `tags: ["faq"]`）。

---

## 給 Agent 的一句話

> 依 AGENTS.md 與 docs/PROMPTS.md 的 **Ingest 提示詞** 處理 `<path>`：歸檔 `raw/sources/`、更新 `wiki/sources`、抽取 concepts／entities、更新 `wiki/index.md`、append `wiki/log.md`。

---

## 檢查清單（第一輪完成後）

- [ ] `raw/sources/` 有新歸檔，且未就地改寫舊檔
- [ ] 每個新 wiki 頁有 frontmatter 與 ≥1 連結
- [ ] 可驗證敘述有 [來源](../sources/....md)（相對路徑）或 `../../raw/sources/*`
- [ ] bundle 內連結為 **相對路徑**（勿用 `/path.md` 根路徑；無 `[[...]]`）
- [ ] `wiki/index.md` 已列出所有新頁
- [ ] `wiki/log.md` 已 append 本輪操作
