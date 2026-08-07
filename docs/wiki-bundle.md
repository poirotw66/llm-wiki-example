# OKF Bundle 導覽

`wiki/` 是純 OKF v0.2 Knowledge Bundle：除了規格保留的 `index.md` 與 `log.md`，每一個 Markdown 檔都是具 YAML frontmatter 與非空 `type` 的 Concept。

操作控制資料不放在 bundle：方向在 [ops/purpose.md](../ops/purpose.md)、人審佇列在 [ops/review-queue.md](../ops/review-queue.md)、Graph 結構洞見預設寫入 `ops/graph-insights.md`。這些檔案不可被 OKF consumer 誤當 Concept。

建立正式 wiki 時，將 `ops/purpose.md` 的 `mode` 改為 `production`，完成目標、問題、範圍與責任人後再執行 lint。
