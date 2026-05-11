# Operations Prompts (Copy-Paste)

Canonical English prompts for Ingest / Query / Lint / FAQ / Graph agents. Logging: every run of an operation defined in `AGENTS.md` must append `wiki/log.md` (use **pass** or **no-op** when no files changed). Update `wiki/index.md` when the operation creates, deletes, or materially changes wiki pages or catalog-listed artifacts (narrower rules per operation in `AGENTS.md`).

---

## Ingest Prompt

Use this repository as a source-grounded wiki system.

Follow `AGENTS.md` strictly:
1. Read the specified source file.
2. Archive it into `raw/sources/*.md` (new file only; do not modify existing files under `raw/`).
3. Create or update `wiki/sources/*` from the archived source using the **Source Page Schema** headings (`Summary`, `Key Concepts`, `Entities`, `Notable Claims`, `Limitations / Gaps`). Scaffold: `docs/templates/page-template-source.md`.
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

Follow `AGENTS.md` Operation: Lint.

Check for:
- contradictions
- stale information
- orphan pages
- missing pages
- duplicate concepts
- pages without sources
- outdated pages

Output results to `wiki/lint/` and include actionable fixes with file-level references. When you add or materially change persisted lint artifacts under `wiki/lint/`, update `wiki/index.md` if the catalog should surface them.

**Always** append `wiki/log.md` for this run (even if no new lint files were written): one line summary, e.g. `pass` or `no issues` or short findings.

---

## FAQ Prompt

Generate reusable FAQ knowledge from the existing wiki.

Follow `AGENTS.md` Operation: FAQ and **FAQ Page Format** / **FAQ Rules**.

1. Read `wiki/index.md`.
2. Scan sources, concepts, entities, and queries pages.
3. Detect repeated patterns, confusing topics, workflows, and cross-page relationships.
4. Produce 8–15 questions (beginner through advanced, including at least one cross-page synthesis question). Do not invent questions with no basis in the wiki.
5. Persist new or updated FAQ pages under `wiki/faq/` using the required frontmatter (`type: query`, `tags: ["faq"]`, etc.) and the Scope / FAQ / Short Answer / Detailed Answer / Related Pages structure.
6. Update `wiki/index.md` (FAQ section: each entry = link + one-line description).
7. Append `wiki/log.md`.

---

## Graph Prompt

Build or refresh knowledge relationships for this wiki.

Follow `AGENTS.md` Operation: Graph.

1. Traverse wiki pages (respect link and relationship rules in `AGENTS.md`).
2. Extract links and infer relationships where appropriate.
3. Generate or update a graph summary (optional artifact example: `wiki/graph/knowledge-map.md`).
4. If you add or materially change persisted graph artifacts, update `wiki/index.md` to link them (e.g. knowledge map).
5. **Always** append `wiki/log.md` for this run — including when output is optional or **unchanged** (record `pass`, `no-op`, or one-line summary per `AGENTS.md`).

---

## Wiki log append (pass / no-op)

Use after any `AGENTS.md` operation when file edits were unnecessary but a trace is still required (e.g. Lint/Graph pass with no new artifacts).

1. Append a new dated section to `wiki/log.md` using the format: `## [YYYY-MM-DD] <operation> | <title>`.
2. One or two bullets: state **pass**, **no-op**, or brief outcome; name the operation (lint / graph / faq / ingest / query persist / etc.).
3. Do not rewrite or delete prior log sections.
