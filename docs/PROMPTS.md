# Operations Prompts（複製貼上）

Ingest／Query／Lint／FAQ／Graph 之標準提示詞。規約見 [**AGENTS.md**](../AGENTS.md)。每次操作套用同一 telemetry wrapper：一開始執行 `python3 scripts/wiki-usage.py start <operation> --title "<本次 log title>"`，append 相同 title 的 `wiki/log.md` 後執行 `python3 scripts/wiki-usage.py finish <operation> --title "<本次 log title>"`；兩者自動記錄 Codex Desktop 實測 token 差額。Telemetry wrapper 不計入各操作的業務步驟。若意外漏掉 `start`，`finish` 會依前一筆有效量測自動復原，且拒絕寫入 0 token 假資料。說明見 [**skill-usage.md**](./skill-usage.md)。若操作新增／刪除／實質變更 wiki 頁或目錄所列產物，更新 `wiki/index.md`。

**Cursor**：可用薄 Skill `/ingest`、`/query`、`/lint`、`/faq`、`/graph`（定義見 [`skills/`](../skills/)；以 `npx skills add` 安裝，見 [README](../README.md#cursor-skill-用法)）觸發；Skill 委派本檔對應章節，**勿在 Skill 內複製步驟**。`.cursor/` 為本機可選副本，**不進 Git**。

---

## Ingest 提示詞

將本 repository 作為以來源為根據的 wiki 系統。完整對照表見 [**docs/ingest-pipeline.md**](./ingest-pipeline.md)。

嚴格遵循 **AGENTS.md** → **操作：Ingest**。步驟 0 為資料治理 gate；telemetry wrapper 不計入業務步驟。開始前讀 [**ops/purpose.md**](../ops/purpose.md)。

開始前：決定本次 `wiki/log.md` title 後，執行 `python3 scripts/wiki-usage.py start ingest --title "<title>"`。
0. **先行資料治理閘**：依 [data-governance.md](./data-governance.md) 判定 classification、owner、access scope、PII、retention、redaction 與 Git 准入。`confidential`／`restricted`、PII 或未知 PII、`redaction: required`、秘密或不確定時，停止自動 Ingest 並要求人工核可。
1. 讀取指定來源；未提供時向使用者索取。
2. **SHA-256 快取**：`python3 scripts/ingest-cache.py lookup "<path>"`。`hit: true` 且未要求強制重跑 → append log **no-op** 並 `finish ingest`。強制重跑時加 `--force` 或使用者明示。
3. **Detect／Triage**：副檔名、是否需轉 Markdown、是否含資訊性視覺。PDF 執行 `scripts/docling-pdf.py` 並讀取 stdout 的 `vision_pages`。
4. 必要時轉為結構化 Markdown。**PDF** 依 [**pdf-ingest-sop.md**](./pdf-ingest-sop.md)（**預設 fast**；僅使用者指定才 `--engine docling`）。視覺閘依 [**visual-source-conversion.md**](./visual-source-conversion.md)；**讀圖一律 subagent**；結束前 lint 不得出現 `weak Visual Evidence`／`Visual Evidence dumped at end`。
   - **自動 Vision（強制）**：若 `vision_pages` **非空**，必須立刻 `--export-vision-assets` 並對每一候選頁派遣 Vision subagent，完成逐頁節點／層級／箭頭盤點與就地 Visual Evidence 後，**才可**建立或更新 wiki 頁（步驟 8 起）。**不可**等待使用者再次指定 Vision，也不可因文字層「看起來夠」而略過候選頁。
   - 僅當 `vision_pages` 為空且無其他資訊圖硬閘時，才可略過 Vision，並在 log／歸檔註明「視覺轉換閘：未適用」。
5. 複製原件至 `raw/originals/`（新檔）。
6. 視覺資產寫入 `raw/assets/`（若適用；`vision_pages` 非空時必做）。
7. **新增** `raw/sources/<archive-slug>.md`（詳盡還原；視覺閘頁須已含就地 Visual Evidence）。
8. **兩段式 · 分析（強制）**：依 [**templates/ingest-analysis.md**](./templates/ingest-analysis.md) 寫入 `.llm-wiki/ingest/analyses/<archive-slug>.md`（實體／概念／既有連結／矛盾與張力／建議落點／review candidates）。將 analysis SHA-256、canonical archive SHA-256、actor、時間與 version 寫入來源頁 `analysis_receipt`，但不提交分析正文。**禁止**未寫分析就產生 wiki 頁；**亦禁止**在 `vision_pages` 尚未跑完 Vision 時產生 wiki 頁。
9. **保證來源摘要頁**：建立／更新 `wiki/sources/<archive-slug>.md`（來源頁 Schema）。每個 raw archive **必須**有對應 wiki 來源頁（lint 硬閘）。
10. 依分析更新 `wiki/concepts/*`、`wiki/entities/*`。
11. 雙向連結（相對路徑）。
12. 補齊 OKF v0.2 + 治理 frontmatter；來源頁填 `archive_slug`。
13. 更新 `wiki/index.md`；有根據時可微調 `ops/purpose.md` → Evolving thesis。
14. **非同步 Review**：`python3 scripts/ingest-review.py append --title "…" --reason "…" --action human_verify|create_page|deep_research|governance|skip [--related path]` → `ops/review-queue.md`（不阻擋寫入）。
15. Append `wiki/log.md`；在 cleanup 前以 lookup digest 記 cache：`python3 scripts/ingest-cache.py record --sha256 "<lookup-sha256>" --original-name "<name>" --archive-slug "<slug>" --source-page "wiki/sources/<slug>.md" --analysis-receipt "<analysis-sha256>" --analysis-source-sha256 "<archive-sha256>" --analysis-generated-by "<actor>" --analysis-generated-at "<ISO-8601>"`。
16. 輸入清理：`scripts/ingest-cleanup.py`（dry-run → `--confirm`）。
完成後：`python3 scripts/wiki-usage.py finish ingest --title "<title>"`。

所有可驗證主張須引用來源；不確定時標記（`（推測）`、`（未知）`）。

---
## Query 提示詞

以可追溯、以來源為根據的流程回答使用者問題。

依序：
0. 決定本次 `wiki/log.md` title 後，執行 `python3 scripts/wiki-usage.py start query --title "<title>"`。
1. 判斷模式：若使用者含「僅讀歸檔」「read sources only」「--sources-only」→ **Read Sources Only**；否則預設模式。先讀 [**ops/purpose.md**](../ops/purpose.md)。
2. **預設模式**：先查 `wiki/` 摘要（優先 **`## Visual Assets`**）；不足／衝突再核對 `raw/sources/*`。
3. **Read Sources Only**：只讀 `raw/sources/*`（必要時 `raw/assets/`／Visual Evidence）；**禁止**把 wiki concepts／entities／faq／queries 當證據；答案標 `mode: read-sources-only`。
4. 答案須含可追溯位置；引用來源；不確定時標記。
5. **視覺答案（強制）**：涉及資訊性視覺時必須 embed `raw/assets/` 或連來源頁；重新讀圖一律 subagent。
6. 可重用則持久化至 `wiki/queries/*` 並更新 index（Read Sources Only 的答案須註明證據僅來自 raw）。
7. **一律** append `wiki/log.md`（含模式；pass／no-op 亦可）。
完成後：`python3 scripts/wiki-usage.py finish query --title "<title>"`。回覆結尾列出 model／tokens／USD；無法量測則標「未量測」。

---
## Lint 提示詞

執行 wiki 品質 Lint，附證據回報。

遵循 **AGENTS.md** → **操作：Lint**。

0. 決定本次 `wiki/log.md` title 後，執行 `python3 scripts/wiki-usage.py start lint --title "<title>"`。
1. **先執行** `uv run --group test python3 scripts/wiki-lint.py`；依 stderr 修正後重跑至 exit 0。
2. 再執行 Agent 深度檢查（見下方清單）。

檢查：矛盾、過時資訊、孤兒頁、缺頁、重複概念、**raw archive 缺 wiki/sources 摘要頁**、過時頁面、**斷鏈**（相對路徑目標不存在）、**`/path.md` 根路徑**（嵌於 repo 時必斷）、**`[[...]]` 混用**（見 **AGENTS.md** → 連結規則）、**視覺資產缺口**（`raw/assets/<base-slug>/` 有圖但對應 `wiki/sources/*` 缺 **`## Visual Assets`** 或缺 `![]()` embed；或 embed 路徑與 `raw/assets/<base-slug>/p<NN>.png` 不一致）、**空殼 Visual Evidence**（canonical `raw/sources/*` 出現「細節以原圖為準」等禁句，或缺層／節點盤點／資料流 — `wiki-lint` 報 `weak Visual Evidence`）、**文末彙整 Visual Evidence**（全部資產 embed 堆在單一 `## Visual Evidence` — 報 `Visual Evidence dumped at end`）。

結果輸出至 `wiki/lint/`，附可執行修正與檔案級引用。**新增或實質變更** lint 產物時，若目錄需露出，更新 `wiki/index.md`（**Overview** 區：連結 + 一行說明）。

**一律** append `wiki/log.md`（即使未寫新 lint 檔）：一行摘要，例如 `pass`、`no issues` 或簡短發現。

完成後執行 `python3 scripts/wiki-usage.py finish lint --title "<title>"`。

---

## FAQ 提示詞

自既有 wiki 產出可重用 FAQ。

遵循 **AGENTS.md** → **操作：FAQ**、**FAQ 頁格式**、**FAQ 規則**。

**空 wiki**：若 `wiki/` 尚無可掃描的 Concept 頁（僅 `index.md`、`log.md` 或各子目錄為空），**勿虛構題目**、勿寫入 `wiki/faq/`；向使用者說明須先 Ingest，並 append `wiki/log.md` 記 **no-op**。

0. 決定本次 `wiki/log.md` title 後，執行 `python3 scripts/wiki-usage.py start faq --title "<title>"`。
1. 讀取 `wiki/index.md`。
2. 掃描 sources、concepts、entities、queries。
3. 偵測重複模式、易混淆主題、流程、跨頁關係。
4. 產出 8–15 題（初階至進階，至少一題跨頁綜合）。勿虛構 wiki 無依據的題目。
5. 持久化至 `wiki/faq/`，使用規定 frontmatter 與 Scope／FAQ／Short Answer／Detailed Answer／Related Pages 結構。
6. 更新 `wiki/index.md`（FAQ 區：連結 + 一行說明）。
7. Append `wiki/log.md`。
完成後：執行 `python3 scripts/wiki-usage.py finish faq --title "<title>"`。

---

## Graph 提示詞

建立或更新本 wiki 知識關係。

遵循 **AGENTS.md** → **操作：Graph**。

**空 wiki**：若尚無 Concept 頁可遍歷，**勿**產出 `wiki/graph/*`；向使用者說明須先累積知識頁，並 append `wiki/log.md` 記 **no-op**（或 **pass**）。

0. 決定本次 `wiki/log.md` title 後，執行 `python3 scripts/wiki-usage.py start graph --title "<title>"`。
1. 遍歷 wiki 頁（遵守連結與關係規則）。
2. 抽取連結並推論關係。
3. 執行 `python3 scripts/wiki-graph-insights.py` → `ops/graph-insights.md`；依 **Agent follow-up** 補充矛盾／缺頁（語意矛盾由 Agent 判斷）。
4. 產出或更新 graph 摘要（可選：`wiki/graph/knowledge-map.md`）。
5. **新增或實質變更** graph 產物時，更新 `wiki/index.md`（**Overview**：連結 + 一行說明，含 insights）。
6. **一律** append `wiki/log.md` — 含可選輸出或 **未變更**（記 `pass`、`no-op` 或一行摘要）。
完成後：執行 `python3 scripts/wiki-usage.py finish graph --title "<title>"`。

---

## Wiki log append（pass／no-op）

**AGENTS.md** 任一操作在 **無須改檔** 但仍須留痕時使用。

1. 以 OKF v0.2 日期分組 append 至 `wiki/log.md`：`## YYYY-MM-DD` 下新增 `- **<operation>** | <title>`，細節用縮排 bullet；同日已有日期標題時只 append 新操作 bullet。
2. 一至兩條 bullet：標 **pass**、**no-op** 或簡述結果。
3. 勿改寫或刪除既有 log 章節。
4. 操作開始／結束的 `start`／`finish` 由各提示詞執行；不可把未知 token／成本填成估算值。

---

## 範例指令

```md
- /ingest <路徑>（或 Cursor 薄 Skill；步驟見本檔 Ingest 提示詞）
- /ingest raw/inbox/某規格.pdf
- Ingest：指定路徑 → triage → raw/sources/*.md → wiki（用上方 Ingest 提示詞）
- Ingest raw/sources/ 下既有檔（每檔一輪；更新 index + log）
- 自現有 wiki 產生 FAQ（8–15 題、勿虛構；用 FAQ 提示詞）
- 回答：<問題>（附引用與不確定性；用 Query 提示詞）
- Lint wiki（用 Lint 提示詞）
- 建立知識 graph（例如 wiki/graph/knowledge-map.md；用 Graph 提示詞）
```
