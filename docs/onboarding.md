# 部門 Wiki 上手（Ingest 流程）

本檔說明 **第一輪 Ingest**。本 repo 的 `wiki/` **刻意留白** — 請以你們自己的第一份文件走完流程。  
**階段 1** 支援 **一鍵多模態**（PDF、Office、圖片等）；完整 12 步對照見 [**ingest-pipeline.md**](./ingest-pipeline.md)。

- 規約：[AGENTS.md](../AGENTS.md)（**OKF 主軸**、**來源轉換政策**）
- OKF 對照：[docs/okf.md](./okf.md)
- Agent 提示詞：[docs/PROMPTS.md](./PROMPTS.md)
- 視覺轉換：[visual-source-conversion.md](./visual-source-conversion.md)
- Skill 入口：[skills/llm-wiki-example/](../skills/llm-wiki-example/SKILL.md)

---

## 採用前：建立部門專用 repo

1. 以 **GitHub Template** 或 **fork** 建立新 repo。
2. **不要**在共用的 `llm-wiki-example` 上寫部門知識。
3. 編輯 `wiki/index.md` 的 **Overview**（部門名稱、範圍、維護方式）。

---

## 假設情境

部門收到內部說明稿（Markdown、PDF、Word、簡報或截圖），要納入 wiki。可將原件丟入 `raw/inbox/`，或在 Cursor 輸入 `/ingest <路徑>`。

---

## 快速流程（對照 12 步）

| 階段 | 做什麼 | 產物 |
|------|--------|------|
| **輸入** | Triage 檔型；必要時轉 Markdown、處理視覺 | `raw/originals/`、`raw/assets/` |
| **歸檔** | 寫入 canonical Markdown | `raw/sources/<slug>.md` |
| **wiki** | 來源頁 + 抽取概念／實體 + 連結 | `wiki/sources/`、`concepts/`、`entities/` |
| **收尾** | 更新目錄與日誌 | `wiki/index.md`、`wiki/log.md` |

詳細步驟編號見 [ingest-pipeline.md](./ingest-pipeline.md)。

---

## 步驟 A：丟檔與歸檔（`raw/`）

1. （可選）將原件放入 `raw/inbox/`。
2. Agent 執行 **Detect／Triage**；非 MD 轉檔後：
   - 原件 → `raw/originals/`
   - 圖片 → `raw/assets/`
   - 正文 → **`raw/sources/<slug>.md`**（新檔；修訂另建新檔）

命名：繁體字面或英文 slug（見 **AGENTS.md**）；範例 `my-api-intro`。

---

## 步驟 B：建立來源頁（`wiki/sources/`）

依 [page-template-source.md](./templates/page-template-source.md) 建立 `wiki/sources/<slug>.md`：

- `type: source`、`resource: "<slug>"`
- Summary、Key Concepts、Entities、Notable Claims、Limitations / Gaps
- Citations：`../../raw/sources/<slug>.md`
- 含視覺時參考歸檔稿 **Visual Evidence** 區塊

---

## 步驟 C：抽取概念與實體

| 類型 | 路徑 | 版型 |
|------|------|------|
| 概念 | `wiki/concepts/<名稱>.md` | [page-template-concept.md](./templates/page-template-concept.md) |
| 實體 | `wiki/entities/<名稱>.md` | 同上（`type: entity`） |

---

## 步驟 D：更新總目錄與日誌

- `wiki/index.md`：各區 **連結 + 一行說明**
- `wiki/log.md`：append 本輪 Ingest（含 triage 摘要）

---

## 步驟 E（可選）：Query 與 FAQ

須先有 wiki 內容。見 **AGENTS.md** → Query／FAQ。

---

## 給 Agent 的一句話

> 依 **docs/PROMPTS.md** Ingest 提示詞處理 `<path>`：triage → `raw/sources/` → `wiki/` → `index` + `log`。

或：`/ingest <path>` · `/ingest raw/inbox/某檔.pdf`

---

## 檢查清單（第一輪完成後）

- [ ] triage／轉檔已記錄（log 或歸檔稿註記）
- [ ] `raw/sources/` 有新歸檔，且未就地改寫舊檔
- [ ] 非 MD 原件在 `raw/originals/`（若適用）
- [ ] 每個新 wiki 頁有 frontmatter 與 ≥1 連結
- [ ] 可驗證敘述有來源引用（相對路徑）
- [ ] bundle 內連結為 **相對路徑**（勿用 `/path.md`）
- [ ] `wiki/index.md` 已列出所有新頁
- [ ] `wiki/log.md` 已 append
