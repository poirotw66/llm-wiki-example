# Operations Prompts (Copy-Paste)

Canonical English prompts for Ingest / Query / Lint agents.

---

## Ingest Prompt

Use this repository as a source-grounded wiki system.

Follow `AGENTS.md` strictly:
1. Read the specified source file.
2. Archive it into `raw/sources/*.md` (new file only; do not modify existing files under `raw/`).
3. Create or update `wiki/sources/*` from the archived source.
4. Extract and update related `wiki/concepts/*` and `wiki/entities/*`.
5. Add bidirectional links where relevant.
6. Update `wiki/index.md`.
7. Append `wiki/log.md`.
8. Mark uncertainty explicitly when needed and cite sources for all claims.

---

## Query Prompt

Answer the user question using a traceable, source-grounded workflow.

Follow this order:
1. Check `wiki/` summary pages first (`faq`, `concepts`, `entities`).
2. If summary information is sufficient and non-conflicting, answer directly.
3. If summary information is insufficient, ambiguous, or conflicting, verify with `raw/sources/*`.
4. Final answers must include traceable locations (at minimum file paths; include section/line anchors when needed).
5. Cite sources and mark uncertainty (`（確定）`, `（推測）`, `（未知）`) when applicable.

---

## Lint Prompt

Run a wiki quality lint pass and report findings with evidence.

Check for:
- contradictions
- stale information
- orphan pages
- missing pages
- duplicate concepts
- pages without sources
- outdated pages

Output results to `wiki/lint/` and include actionable fixes with file-level references.
