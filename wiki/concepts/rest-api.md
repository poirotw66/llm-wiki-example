---
title: "REST API"
type: concept
status: active
updated: "2026-06-17"
source_count: 1
tags: ["api", "範例"]
description: "【範例】部門內 REST 風格約定：版本路徑、JSON、JWT、統一錯誤 envelope 與冪等 POST。"
timestamp: "2026-06-17T00:00:00Z"
---

# REST API

> **【範例】** 以下為依虛構《訂單 API 簡介》收斂之部門慣例摘要，非全公司正式標準。

## Summary

部門對外 HTTP API 採 **REST 風格**：以資源路徑與 HTTP 動詞表達操作，路徑常含版本前綴（如 `/v1`），請求／回應主體為 `application/json`。（確定）[訂單 API 簡介](../sources/訂單-api-簡介.md)

## Key Points

- **動詞與語意**：建立資源用 POST（如 POST `/orders`）；讀取用 GET；具副作用的狀態轉換可用 POST 子資源（如 `/cancel`）。（確定）[訂單 API 簡介](../sources/訂單-api-簡介.md)
- **認證**：`Authorization: Bearer <JWT>`；依 scope 區分讀寫（例：`orders:read`、`orders:write`）。（確定）[訂單 API 簡介](../sources/訂單-api-簡介.md)
- **錯誤 envelope**：失敗時回 JSON `{ "error": { "code", "message", "request_id" } }`，並以 HTTP 狀態表達類別（4xx／5xx）。（確定）[訂單 API 簡介](../sources/訂單-api-簡介.md)
- **冪等寫入**：建立類 POST 建議接受 `idempotency_key`，避免客戶端重試造成重複資源。（確定）[訂單 API 簡介](../sources/訂單-api-簡介.md)
- **列表查詢**：GET 集合端點支援查詢參數篩選（稿內例：`status`、`created_after`）。（確定）[訂單 API 簡介](../sources/訂單-api-簡介.md)
- **速率限制**：超限回 429，並以 `Retry-After` 提示重試間隔。（確定）[訂單 API 簡介](../sources/訂單-api-簡介.md)

## Evidence

- 訂單服務 API 為本部門 REST 實作範例：端點表、建單 JSON、錯誤格式均見來源稿。[訂單 API 簡介](../sources/訂單-api-簡介.md)

## Relationships

- related_to: [訂單服務](../entities/訂單服務.md)
- used_in: [訂單 API 簡介](../sources/訂單-api-簡介.md)

## Open Questions

- 部門是否已發布跨服務統一的 **分頁** 參數命名（`page`／`cursor`）？來源稿僅提及列表篩選。（未知）
- GraphQL 或 gRPC 內部服務是否豁免 REST envelope？（未知）
