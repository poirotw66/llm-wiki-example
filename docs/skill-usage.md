# Skill 實際 token 使用量追蹤

本倉以 `.llm-wiki/usage/events.jsonl` 保存 append-only telemetry。當 Agent 在 **Codex Desktop** 執行 LLM Wiki 流程時，Skill 會在操作開始與結束自動讀取 Codex session JSONL 的 `token_count.last_token_usage`，將每次 turn 的 input、cached input、cache writes、output、reasoning、total 與 model 歸因給本次 Ingest／Query／Lint／FAQ／Graph。

這是 Codex session runtime 的每-turn usage，不是由 `wiki/log.md` 猜測的數字。`wiki/log.md` 仍用於人類可讀的結果與補齊舊操作的「次數」紀錄；沒有量測快照的歷史事件會顯示 `—`，不再顯示為 `0`。

## 日常使用

使用者不需要手動下任何追蹤指令，照常執行 `/ingest`、`/query`、`/lint`、`/faq`、`/graph` 即可。各 Skill 依流程自動呼叫。為避免 agent 漏掉開始快照，`finish` 現在具備自癒機制：會以最近一筆有效量測作為邊界重新計算；找不到可靠邊界時直接不寫事件，絕不把 0 token 當成實際費用。

```bash
# 操作開始時（title 與 wiki/log.md 標題相同）
uv run python scripts/wiki-usage.py start <operation> --title "<operation title>"

# 寫完 wiki/log.md 後
uv run python scripts/wiki-usage.py finish <operation> --title "<operation title>"
```

`--title` 讓完成時能對應正確的 `wiki/log.md` 條目，即使另一個 task 同時 append log 也不會誤歸因。若本機不是 Codex Desktop，或找不到對應 task，流程不會失敗；該次仍由 `wiki/log.md` 計入執行次數，但 token 顯示 `—`。

每次 `finish` 也會直接印出本次的 model 與 `cost=USD`；因此 Query／Ingest 回覆可以直接附上這筆量測結果。

## 報表

```bash
uv run python scripts/wiki-usage.py report --by operation
uv run python scripts/wiki-usage.py report --by skill
uv run python scripts/wiki-usage.py report --by model
uv run python scripts/wiki-usage.py report --by operation --format json
```

`Total tokens` 及 input／output／cache 欄位來自每次 session 的 `last_token_usage`；當欄位完整時，報表以事件的實際 model 讀取 [`config/skill-usage-pricing.json`](../config/skill-usage-pricing.json)，顯示精確的 **API equiv. USD**。只有舊的總 token 快照才會顯示費用區間；這不是 Codex 訂閱實際扣款。

要看每一次 Ingest／Query 的個別費用，可依 log title 展開：

```bash
uv run python scripts/wiki-usage.py report --by run
```

要看兩類操作的彙總則使用 `--by operation`；每筆已完成的操作都會有自己的 token、model、耗時與成本事件。

目前設定 GPT-5.6 Sol／Terra／Luna 的 API 定價；費率來源為 [OpenAI model catalog](https://developers.openai.com/api/docs/models)。更新費率時只需修改 pricing JSON。

## 直接查看 ccusage 同等資料

不只看 LLM Wiki 五大流程，也可以直接查看目前 workspace 的所有 Codex session turn：

一條指令會依序顯示 model、day、session 三個區段：

```bash
uv run python scripts/wiki-usage.py codex-report
```

需要單獨查看某一種分組時才加 `--by`；需要機器可讀輸出時加 `--format json`：

```bash
uv run python scripts/wiki-usage.py codex-report --by model
uv run python scripts/wiki-usage.py codex-report --format json
```

這些欄位對應 ccusage 的 Codex 資料模型：`input_tokens`、`cached_input_tokens`、`cache_write_input_tokens`、`output_tokens`、`reasoning_output_tokens`、`total_tokens`、model、session 與 USD cost。ccusage 同樣是從 Codex session JSONL 的累計 token event 取每次 turn 的差額／usage，並依 model 計價。[ccusage Codex data source](https://ccusage.com/guide/codex/)

## 資料邊界

- 同一 session 同時進行其他對話或工作時，時間區間內的 turn 可能落在該操作；`--title` 綁定 log 條目避免跨流程誤歸因。
- token 量測使用 Codex session JSONL；其他 Agent runtime 沒有相容 JSONL 時，不能憑空估算。
- 不記錄提問內容、來源內容、密碼或個資。事件只含操作、Skill、模型、量測 token、耗時及狀態。
- `record` 僅供有供應商原始量測資料的整合使用；不可手動猜測 token 或成本。
