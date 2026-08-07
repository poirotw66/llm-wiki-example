# Ingest analysis template（兩段式 Ingest · 步驟 A）

寫入路徑：`.llm-wiki/ingest/analyses/<archive-slug>.md`（私有、gitignore 工作產物；**不可進 Git**）。完成後只將 analysis SHA-256、canonical `raw/sources` SHA-256、actor 與時間寫入 `wiki/sources` 的 `analysis_receipt`。
**必須先完成此分析，再寫 `wiki/sources|concepts|entities`。**

```md
# Ingest analysis — <archive-slug>

- source: <input path or raw/originals/…>
- sha256: <hex>
- engine: fast | docling
- analyzed_at: <ISO 8601>

## Entities to create or update

- <name> — why；suggested path `wiki/entities/….md`

## Concepts to create or update

- <name> — why；suggested path `wiki/concepts/….md`

## Links to existing wiki

- related: [existing page](../../wiki/…) — how this source connects

## Contradictions / tensions

- （無）或：與 [page](…) 可能衝突：…

## Suggested wiki layout

- source page: `wiki/sources/<archive-slug>.md`（**必有**）
- concepts: …
- entities: …

## Review candidates（非阻塞）

- title: …
  reason: …
  suggested_action: human_verify | create_page | deep_research | governance | skip
```
