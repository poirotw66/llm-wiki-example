---
title: "訂單 API 簡介"
type: source
status: active
updated: "2026-06-17"
source_count: 1
tags: ["api", "訂單", "範例"]
description: "【範例】虛構內部稿：訂單服務 v1 REST API、認證、端點與錯誤格式摘要。"
resource: "raw/sources/訂單-api-簡介.md"
timestamp: "2026-06-17T00:00:00Z"
---

# 訂單 API 簡介

> **【範例】** 本頁與歸檔稿內容均為虛構，僅供示範 Ingest 後之來源頁樣貌；部門 fork 後請刪除或覆寫。

## Summary

- 訂單服務（order-service）對外提供 REST API，路徑前綴 `/v1`；正式 Base URL 為 `https://api.example.internal/v1`。（確定）[[sources/訂單-api-簡介]]
- 認證採 Bearer JWT，scope 須含 `orders:read` 或 `orders:write`；未授權 401、權限不足 403。（確定）[[sources/訂單-api-簡介]]
- 核心端點：POST `/orders` 建單、GET `/orders/{order_id}` 查單、GET `/orders` 列表、POST `/orders/{order_id}/cancel` 取消（僅 `PENDING`）。（確定）[[sources/訂單-api-簡介]]
- 建單支援 `idempotency_key`，重送相同 key 回傳相同 `order_id`。（確定）[[sources/訂單-api-簡介]]
- 錯誤回應為統一 JSON envelope（`error.code`、`error.message`、`request_id`）。（確定）[[sources/訂單-api-簡介]]

## Key Concepts

- [[concepts/rest-api]] — 本部門 HTTP 資源型 API 與錯誤 envelope 約定
- **冪等建單** — POST 透過 `idempotency_key` 避免重複下單（稿內實例）（確定）[[sources/訂單-api-簡介]]

## Entities

- [[entities/訂單服務]] — 實作上述 API 的後端服務（虛構示範實體）

## Notable Claims

- 建立訂單成功回 **201**，body 含 `order_id`、`status`（初值 `PENDING`）、`total_amount`、`currency`、`created_at`。（確定）[[sources/訂單-api-簡介]]
- 速率限制：每 API Key **600 req/min**，超限 **429** 並附 `Retry-After`。（確定）[[sources/訂單-api-簡介]]
- 常見錯誤狀態碼含 400、404、409（狀態衝突）、429。（確定）[[sources/訂單-api-簡介]]
- 完整規格指向內部「訂單服務 API v2」；本稿為 v1.3 簡介，未含 v2 全部欄位。（確定）[[sources/訂單-api-簡介]]

## Limitations / Gaps

- 歸檔稿自述未附完整 schema、列舉值與 Webhook（`order.shipped`）說明。（確定）[[sources/訂單-api-簡介]]
- 熔斷／降級策略僅提及在維運手冊，本文未收錄。（確定）[[sources/訂單-api-簡介]]
- 本 wiki 頁未驗證 OpenAPI v2 是否存在 — 屬虛構情境。（推測）

## Relationships

- related_to: [[concepts/rest-api]]
- used_in: [[entities/訂單服務]]

# Citations

[1] [歸檔稿 v1.3](raw/sources/訂單-api-簡介.md)（`resource` 指向同一路徑）
