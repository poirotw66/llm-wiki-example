# 部門 Wiki 上手（Ingest 流程）

本檔說明 **第一輪 Ingest** 步驟。本 repo 的 `wiki/` **刻意留白** — 請以你們自己的第一份文件走完流程；頁面版型見 [docs/templates/](./templates/)。

- 規約：[AGENTS.md](../AGENTS.md)（**OKF 主軸**）
- OKF 對照：[docs/okf.md](./okf.md)
- Agent 提示詞：[docs/PROMPTS.md](./PROMPTS.md)
- Skill 入口：[skills/llm-wiki-example/](../skills/llm-wiki-example/SKILL.md)

---

## 採用前：建立部門專用 repo

1. 以 **GitHub Template** 或 **fork** 建立新 repo。
2. **不要**在共用的 `llm-wiki-example` 上寫各部門知識。
3. 編輯 `wiki/index.md` 的 **Overview**（部門名稱、範圍、維護方式）。

---

## 假設情境

部門收到內部說明稿（例如 `docs/內部-api-簡介.md` 或 Confluence 匯出），要納入 wiki。

---

## 步驟 1：歸檔來源（`raw/sources/`）

將指定來源 **新增** 至 `raw/sources/<slug>.md`（`<slug>` 與檔名一致，不含 `.md`）。日後修訂來源時 **另建新歸檔檔**，勿改寫既有 `raw/` 檔。

命名：依 **AGENTS.md** 使用繁體字面或英文識別名，**勿**用漢語拼音。範例 slug：`my-api-intro` → `raw/sources/my-api-intro.md`。

---

## 步驟 2：建立來源頁（`wiki/sources/`）

依 [page-template-source.md](./templates/page-template-source.md) 建立 `wiki/sources/<slug>.md`：

- frontmatter `type: source`、`resource: "<slug>"`（與歸檔 slug 一致）
- 必填區塊：Summary、Key Concepts、Entities、Notable Claims、Limitations / Gaps
- Citations 連結歸檔：`../../raw/sources/<slug>.md`

---

## 步驟 3：抽取概念與實體

| 類型 | 路徑 | 版型 |
|------|------|------|
| 概念 | `wiki/concepts/<名稱>.md` | [page-template-concept.md](./templates/page-template-concept.md)（`type: concept`） |
| 實體 | `wiki/entities/<名稱>.md` | 同上（`type: entity`；建議填 `resource`） |

區塊骨架見 **AGENTS.md** → **Concept／Entity／Query／Lint 頁**。

---

## 步驟 4：更新總目錄（`wiki/index.md`）

於 **Concepts**、**Entities**、**Sources** 等區各加 **連結 + 一行說明**；移除「尚無內容」佔位句。

---

## 步驟 5：append 操作日誌（`wiki/log.md`）

自第一次真實操作起 append（格式見 **AGENTS.md** → **Logging Rules**）。

---

## 步驟 6（可選）：Query 與 FAQ

| 需求 | 路徑 | 版型 |
|------|------|------|
| 單一可重用問答 | `wiki/queries/<問題>.md` | `page-template-concept.md`（`type: query`） |
| 題組（8–15 題） | `wiki/faq/<主題>.md` | 同上 + `tags: ["faq"]`；格式見 **AGENTS.md** → **FAQ 頁格式** |

---

## 給 Agent 的一句話

> 依 AGENTS.md 與 docs/PROMPTS.md 的 **Ingest 提示詞** 處理 `<path>`：歸檔 `raw/sources/`、更新 `wiki/sources`、抽取 concepts／entities、更新 `wiki/index.md`、append `wiki/log.md`。

或在 Cursor 輸入：`/ingest <path>`

---

## 檢查清單（第一輪完成後）

- [ ] `raw/sources/` 有新歸檔，且未就地改寫舊檔
- [ ] 每個新 wiki 頁有 frontmatter 與 ≥1 連結
- [ ] 可驗證敘述有來源引用（相對路徑 `../sources/....md` 或 `../../raw/sources/*`）
- [ ] bundle 內連結為 **相對路徑**（勿用 `/path.md` 根路徑；無 `[[...]]`）
- [ ] `wiki/index.md` 已列出所有新頁
- [ ] `wiki/log.md` 已 append 本輪操作
