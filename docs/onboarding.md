# 部門 Wiki 上手（Ingest 流程）

本檔說明 **第一輪 Ingest**。本 repo 的 `wiki/` **刻意留白** — 請以你們自己的第一份文件走完流程。  
**階段 1** 支援 **一鍵多模態**（PDF、Office、圖片等）；完整 13 個 Ingest 業務步驟見 [**ingest-pipeline.md**](./ingest-pipeline.md)（telemetry 為外層 wrapper）。

- 規約：[AGENTS.md](../AGENTS.md)（**OKF 主軸**、**來源轉換政策**）
- OKF 對照：[docs/okf.md](./okf.md)
- Agent 提示詞：[docs/PROMPTS.md](./PROMPTS.md)
- 視覺轉換：[visual-source-conversion.md](./visual-source-conversion.md)
- PDF 轉譯 SOP：[pdf-ingest-sop.md](./pdf-ingest-sop.md)（含 **前置（安裝）**：`uv sync --group pdf` + 模型下載至 `models/docling/` + Poppler）
- 初始化安裝建議指令：[README.md → 初始化安裝](../README.md#初始化安裝建議含-pdf-ingest)
- Skill 入口：[skills/llm-wiki-example/](../skills/llm-wiki-example/SKILL.md)

---

## 採用前：建立部門專用 repo

1. 以 **GitHub Template** 或 **fork** 建立新 repo。
2. **不要**在共用的 `llm-wiki-example` 上寫部門知識。
3. 編輯 `wiki/index.md` 的 **Overview**（部門名稱、範圍、維護方式）。
4. 先指定資料 owner、分類／PII 規則與核准私有 repo；依 [data-governance.md](./data-governance.md) 完成 Git 准入與例外流程設定。
5. 若會 ingest PDF：完成下方 **PDF 前置（與 README 對齊）**（約 1.2GB 模型，不進 Git）。

### PDF 前置（與 README 對齊）

完整指令見 [README 初始化安裝](../README.md#初始化安裝建議含-pdf-ingest)。摘要：

```bash
uv sync --group pdf
uv run docling-tools models download -o models/docling
# Poppler：macOS brew / Ubuntu apt / Windows winget（oschwartz10612.Poppler）
uv run python scripts/docling-pdf.py --help
pdfinfo -v
```

Windows 注意：用 `uv run python`（勿依賴 Store 的 `python3`）；安裝 Poppler 後**重開終端**讓 PATH 生效。

### 輸入偏好（文字層優先）

- **優先**：可選取文字的 PDF、Markdown、Word／簡報（文字層完整 → Docling／文字直入，vision 只打資訊圖頁）。
- **避免當首選**：純圖／掃描／整頁點陣簡報（文字層 0 → 幾乎全頁 vision，成本高、較易空殼需重派）。
- 若只有純圖 PDF，仍可 ingest，但請預期較久，並依 [visual-source-conversion.md](./visual-source-conversion.md) 做 vision 驗收／自動重派。
- **OCR**：Docling OCR 對繁中簡報常不穩。文字層空時 **以 vision 為正文**，不必為 OCR 調參；細節見 [pdf-ingest-sop.md → OCR 策略](./pdf-ingest-sop.md#ocr-策略刻意不硬優化)。

---

## 部分頁 Ingest（第一次用建議）

長 PDF 可先只收一段，確認流程再全檔。

**跟 Agent 說：**

```text
/ingest raw/inbox/手冊.pdf 第 1–5 頁
/ingest ./架構說明.pdf 前五頁
```

**預期產物：**

- `raw/sources/<base-slug>-頁1至5.md`
- 資產仍在 `raw/assets/<base-slug>/p01.png`…（頁碼 = PDF 實際頁）
- Limitations 註明未涵蓋頁

完整互動範例與 checklist：[pdf-ingest-sop.md → 部分頁 Ingest](./pdf-ingest-sop.md#部分頁-ingest第一次用)。

---

## 假設情境

部門收到內部說明稿（Markdown、PDF、Word、簡報或截圖），要納入 wiki。可將原件丟入 `raw/inbox/`，或在 Cursor 輸入 `/ingest <路徑>`。

---

## 快速流程（對照 13 個業務步驟）

| 階段 | 做什麼 | 產物 |
|------|--------|------|
| **輸入** | Triage；**一律**複本至 originals（含 MD）；必要時轉檔／視覺 | `raw/originals/`、`raw/assets/` |
| **歸檔** | 寫入 canonical Markdown 歸檔稿 | `raw/sources/<archive-slug>.md` |
| **wiki** | 來源頁 + 抽取概念／實體 + 連結 | `wiki/sources/`、`concepts/`、`entities/` |
| **收尾** | 更新目錄與日誌 | `wiki/index.md`、`wiki/log.md` |

詳細步驟編號見 [ingest-pipeline.md](./ingest-pipeline.md)。

---

## 步驟 A：丟檔與歸檔（`raw/`）

1. （可選）將原件放入 `raw/inbox/`。
2. Agent 先執行 [資料治理閘](./data-governance.md)：`confidential`／`restricted`、PII、未知 PII、待遮罩或疑似秘密資料，未經人工核可不可寫入 `raw/`、Git 或外部轉檔工具。
3. Agent 執行 **Detect／Triage**；**PDF** 依 [pdf-ingest-sop.md](./pdf-ingest-sop.md)。**所有已准入輸入**（含 `.md`）先：
   - 原件 → `raw/originals/`（位元副本）
   - 圖片（若有）→ `raw/assets/<base-slug>/p<NN>.png`
   - canonical 正文 → **`raw/sources/<archive-slug>.md`**（新檔；修訂另建新檔）
4. 歸檔成功後，依 cleanup dry-run／`--confirm` 防呆流程 **刪除** `raw/inbox/` 或 repo 根目錄的輸入副本（原件已在 `raw/originals/`；見 **ingest-pipeline** 步驟 12）。

命名：`<base-slug>`（資產用）、`<archive-slug>`（歸檔檔名與 `resource`）；全檔／部分頁／修訂規則見 **pdf-ingest-sop.md** 與 **AGENTS.md**。

---

## 步驟 B：建立來源頁（`wiki/sources/`）

依 [page-template-source.md](./templates/page-template-source.md) 建立 `wiki/sources/<slug>.md`：

- `type: source`、`archive_slug: "<slug>"`、`sources`（指向歸檔稿）、`generated`、OKF v0.2 lifecycle 與六個治理欄位
- Summary、Key Concepts、Entities、Notable Claims、**Visual Assets**（有圖時 embed 原圖）、Limitations / Gaps
- 以 `sources[].resource: "../../raw/sources/<slug>.md"` 與 keyed footnote 記錄 provenance
- 含視覺時：`## Visual Assets` 須 `![]()` 指向 `../../raw/assets/<base-slug>/p<NN>.png`；詳見 **visual-source-conversion.md**

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

## 回到範本空白（可選）

若要清除 knowledge／raw 歸檔並還原空白目錄（**保留** `wiki/lint/`）：

```bash
uv run python scripts/wiki-reset.py          # dry-run
uv run python scripts/wiki-reset.py --confirm
```

---

## 檢查清單（第一輪完成後）

- [ ] 輸入原件已清理（inbox／根目錄副本已刪，若適用）
- [ ] `raw/sources/` 有新歸檔，且未就地改寫舊檔
- [ ] 輸入原件已在 `raw/originals/`（**含** Markdown）
- [ ] canonical 歸檔稿在 `raw/sources/`
- [ ] 資料分類、owner、access scope、PII、retention 與 redaction 已人工確認；Git 准入已通過
- [ ] 每個新 wiki 頁有 frontmatter 與 ≥1 連結
- [ ] 可驗證敘述有來源引用（相對路徑）
- [ ] bundle 內連結為 **相對路徑**（勿用 `/path.md`）
- [ ] `wiki/index.md` 已列出所有新頁
- [ ] `wiki/log.md` 已 append
