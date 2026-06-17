# 訂單 API 簡介

| 欄位 | 內容 |
|------|------|
| 文件版本 | v1.3（2026-05-20） |
| 服務 | 訂單服務（order-service） |
| 維護團隊 | 交易平台後端（虛構） |
| 狀態 | **範例 repo 虛構稿** — fork 後請以真實 Confluence／OpenAPI 替換 |

---

## 1. 概述

訂單服務負責建立、查詢與取消訂單。對外提供 **REST API**，路徑前綴 `/v1`。正式環境 Base URL：

`https://api.example.internal/v1`

（以上網域與團隊名稱均為示範用虛構資料。）

## 2. 認證

所有請求須帶 `Authorization: Bearer <JWT>`。Token 由部門 SSO 發行，scope 須含 `orders:read` 或 `orders:write`。

未帶 Token 回 **401**；scope 不足回 **403**。

## 3. 端點摘要

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/orders` | 建立訂單 |
| GET | `/orders/{order_id}` | 查詢單筆 |
| GET | `/orders` | 列表（支援 `status`、`created_after` 查詢參數） |
| POST | `/orders/{order_id}/cancel` | 取消訂單（僅 `PENDING` 可取消） |

完整 OpenAPI 規格見內部「訂單服務 API v2」— 本簡介稿尚未納入 v2 全部欄位（見 §6 缺口）。

## 4. 建立訂單 — POST /orders

**Request（application/json）**

```json
{
  "customer_id": "cus_8f2a",
  "items": [
    { "sku": "BOOK-001", "quantity": 2, "unit_price": 350 }
  ],
  "currency": "TWD",
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response 201**

```json
{
  "order_id": "ord_7k3m9x",
  "status": "PENDING",
  "total_amount": 700,
  "currency": "TWD",
  "created_at": "2026-05-20T08:15:30Z"
}
```

重送相同 `idempotency_key` 時回傳相同 `order_id`，不重複建單。

## 5. 錯誤格式

錯誤回應統一為：

```json
{
  "error": {
    "code": "INVALID_SKU",
    "message": "SKU not found in catalog",
    "request_id": "req_a1b2c3"
  }
}
```

常見 HTTP 狀態：**400** 參數錯誤、**404** 訂單不存在、**409** 狀態衝突（例如已出貨不可取消）、**429** 超過速率限制。

## 6. 速率限制

每 API Key 每分鐘 **600** 次請求；超限回 429，`Retry-After` header 指示秒數。

## 7. 已知缺口（稿內自述）

- 未附完整欄位 schema 與列舉值說明。
- Webhook（`order.shipped`）事件未在本簡介涵蓋。
- 正式環境熔斷與降級策略見維運手冊，本文未收錄。
