# 📘 LLM Wiki Schema

You are the maintainer of this wiki. Treat this repository as a **persistent, graph-aware, source-grounded knowledge system**.

---

# 🎯 System Goal

Build a **self-evolving knowledge base** that:

* Minimizes hallucination
* Maximizes traceability
* Maintains structured relationships (graph)
* Supports reuse (FAQ, onboarding, RAG, agents)

---

# 🧠 Core Principles

* Source-grounded > Speculation
* Structure > Volume
* Links > Isolation
* Evolution > Perfection

---

# 📁 Directory Contract

* `raw/`: immutable **existing** sources (❗ do not edit in place). **New** files may be **archived** into `raw/sources/` as step 2 of Ingest.

* `raw/assets/`: optional images / attachments referenced from sources or wiki pages (not parsed as knowledge pages; add new files during Ingest or maintenance as needed).

* `wiki/`: LLM-managed knowledge base

* `wiki/index.md`: canonical catalog

* `wiki/log.md`: append-only log

* `wiki/sources/`: parsed source knowledge

* `wiki/concepts/`: abstract ideas (MVC, API, Transaction)

* `wiki/entities/`: concrete systems (Vue, Spring Boot, JDBC)

* `wiki/queries/`: reusable **single** Q&A pages (one question → one persisted answer)

* `wiki/faq/`: structured **FAQ collections** (8–15 questions per page; frontmatter `type: query` with `tags: ["faq"]` — the `type` value reflects page shape, not the `wiki/queries/` folder)

* `wiki/lint/`: diagnostics

* `wiki/graph/`: relationship mappings (optional advanced)

* `docs/` (**supporting files**, not part of the wiki knowledge corpus):

  * `docs/templates/page-template-source.md` — scaffold for **`wiki/sources/*`** only; section headings MUST match **Source Page Schema** below exactly.

  * `docs/onboarding.md` — **non-wiki** walkthrough with fictional sample paths; includes inline examples for concept / entity pages.

  * **Operations Prompts (Copy-Paste)** — English agent prompts for Ingest / Query / Lint / FAQ / Graph live in **this file** under **Operations Prompts (Copy-Paste)** below; maintain them here as the single source of truth.

---

# 🧱 Wiki Page Conventions

* Markdown only

* Must include YAML frontmatter on wiki pages **except** `wiki/index.md` (catalog — see **Required Frontmatter** below)

* Language: **Traditional Chinese**

* English only for technical terms (API, MVC, Vue...)

* Writing style:

  * concise
  * structured
  * verifiable

* **檔案與路徑命名**（`wiki/**`、Ingest 新增之 `raw/sources/*.md` 等由本 wiki 決定之檔名）：

  * 使用**繁體中文**或**英文**（含技術詞、既有目錄沿用之 slug，例如 `concepts/api`）。
  * **勿**以**漢語拼音**拼寫中文語意作為檔名或路徑片段：對台灣讀者不直觀，也與本地慣用之書寫系統不一致；應改為繁體字面，或改用具辨識度之英文識別名。

---

# 📌 Required Frontmatter

```yaml
---
title: "<Page title>"
type: "<overview|entity|concept|source|query|lint>"
status: "<draft|active|needs-review>"
updated: "YYYY-MM-DD"
source_count: 0
tags: []
---
```

### `wiki/index.md` (catalog)

* **YAML frontmatter is optional** for this file. The required shape is the **Index Structure** heading layout (`# Index`, `## Overview`, …); do not fail compliance for missing frontmatter here.
* The `type: "overview"` value in the schema is for **standalone** overview pages if you add them (e.g. team-specific `wiki/overview.md`); it is **not** required for `wiki/index.md`.
* If you choose to add frontmatter to `wiki/index.md`, use the same keys as **Required Frontmatter** (e.g. `type: overview`, `title` describing the catalog).

---

# 🔗 Linking Rules (MANDATORY)

* Every page MUST link to ≥1 page
* Every new page MUST be referenced
* Prefer bidirectional links

### Wiki link convention

* In wiki prose, use wiki-style links without the `wiki/` prefix, e.g. `[[sources/example]]`, `[[concepts/api]]`, `[[entities/spring-boot]]`.
* Resolve paths relative to `wiki/` (the file is `wiki/sources/example.md`, etc.).
* When linking to the catalog or support docs from a wiki page, `[[../index]]` (i.e. `wiki/index.md`) and pointers to repo-root **`AGENTS.md`** or **`docs/onboarding.md`** are valid targets.

### Cold start (empty wiki)

* Before the first knowledge pages exist, the skeleton has no wiki pages to cross-link. After the **first Ingest**, every new page should link to at least one other wiki page (typically `wiki/index.md` via `[[../index]]` or reciprocal links among source / concept / entity pages).

---

# 🧩 Knowledge Graph Rules

Every page should implicitly or explicitly define relationships:

### Allowed Relationships

* `concept → concept`
* `concept → entity`
* `entity → concept`
* `source → concept/entity`

### Optional explicit section:

```md
## Relationships

- related_to: [[concepts/api]]
- implemented_by: [[entities/spring-boot]]
- used_in: [[sources/ch1]]
```

👉 This enables graph-based reasoning later (RAG / agents)

---

# 📏 Page Granularity Rules

* One page = one concept / entity
* > 500 words → split
* Do NOT mix abstraction layers

---

# 📌 Citation Rules (CRITICAL)

* All claims must cite sources

Format:

```md
[[sources/ch1]]
```

Multiple:

```md
[[sources/ch1]], [[sources/ch3]]
```

---

# ⚠️ Uncertainty Markers

* （確定）
* （推測）
* （未知）

---

# 📚 Source Page Schema

Each `wiki/sources/*` must include:

```md
## Summary
- 3–5 bullets

## Key Concepts

## Entities

## Notable Claims

## Limitations / Gaps
```

Starter scaffold for source pages: **`docs/templates/page-template-source.md`**.

---

# 📄 Concept / Entity / Query / Lint Pages (suggested scaffold)

For **`wiki/concepts/*`**, **`wiki/entities/*`**, **`wiki/queries/*`**, and **`wiki/lint/*`**: use **Required Frontmatter**; section names below are **suggested** (not as strict as **Source Page Schema**). Set `type` to `concept` | `entity` | `query` | `lint`. Cite sources for grounded claims.

```yaml
---
title: "<Page title>"
type: concept
status: draft
updated: "YYYY-MM-DD"
source_count: 1
tags: []
---
```

```md
# <Page title>

## Summary

One paragraph overview.

## Key Points

- Point with citation [[sources/...]]

## Evidence

- Grounded claim → [[sources/...]] or `raw/sources/*`

## Relationships

- related_to: [[concepts/...]]
- implemented_by: [[entities/...]]

## Open Questions

- Optional follow-ups
```

FAQ pages under `wiki/faq/` use **FAQ Page Format** below (not this scaffold). A worked example for concept / entity paths: **`docs/onboarding.md`** step 3.

---

# 📑 Index Structure

The canonical catalog is **`wiki/index.md`** (single file). Do **not** assume a separate `wiki/overview.md` unless your team adds one by convention; by default, **all index sections below—including Overview—live in `wiki/index.md`**, in this order:

```md
# Index

## Overview
## Concepts
## Entities
## Sources
## Queries
## FAQ
```

* **`## Overview`**: Short orientation only (scope, how to use this wiki, pointers to repo-root **`AGENTS.md`** and **`wiki/README.md`** when present). Use a few bullets; do not duplicate the full taxonomy—**Concepts** onward hold the linked catalog. **Maintenance artifacts** (e.g. `wiki/lint/*` summaries, `wiki/graph/knowledge-map.md`) are also linked here as **link + one-line description** bullets when the team wants them in the catalog—there is no separate `## Lint` / `## Graph` index section by default.
* **`## Concepts` … `## FAQ`**: Each entry = **link + one-line description** (per section).

---

# 🛠 Operation: Ingest

1. Read the **specified** source file (path or artifact provided for this ingest).
2. **Archive** it into `raw/sources/*.md` (new file only; stable name per team convention; follow **檔案與路徑命名** in Wiki Page Conventions). **Do not** overwrite or in-place edit existing files under `raw/` unless explicitly approved.
3. Create/update `wiki/sources/` from that archived file under `raw/sources/`.
4. Extract:

   * concepts
   * entities
5. Update related pages
6. Link everything
7. Update index
8. Append log

---

# ❓ Operation: Query

1. Read index
2. Find relevant pages
3. Synthesize answer
4. Cite sources
5. Mark uncertainty
6. If the answer is reusable, persist under `wiki/queries/*` and update `wiki/index.md` (**Queries** section).
7. **Always** append `wiki/log.md` for this run (use **pass** / **no-op** when the session was answer-only with no new or updated wiki pages).

## Query Resolution Rule (MANDATORY)

1. Check `wiki/` summary pages first (`faq`, `concepts`, `entities`, `queries`).
2. If summary information is sufficient and non-conflicting, answer directly.
3. If summary information is insufficient, ambiguous, or conflicting, verify with `raw/sources/*`.
4. Final answers MUST include traceable locations (at minimum file paths; include section/line anchors when needed).

---

# 📚 Operation: FAQ

## Purpose

Generate reusable knowledge from existing wiki

---

## Steps

1. Read `wiki/index.md`
2. Scan:

   * sources
   * concepts
   * entities
   * queries
3. Detect:

   * repeated patterns
   * confusing topics
   * workflows
   * cross-page relationships
4. Generate FAQ (basic → advanced)
5. Persist new or updated FAQ pages under `wiki/faq/`
6. Update `wiki/index.md` (FAQ section: each entry = link + one-line description)
7. Append `wiki/log.md`

---

## FAQ Page Format

```yaml
---
title: "<FAQ title>"
type: "query"
status: "active"
updated: "YYYY-MM-DD"
source_count: 0
tags: ["faq"]
---
```

```md
# <FAQ Title>

## Scope

說明範圍

## FAQ

### 1. 問題

**Short Answer：**  

**Detailed Answer：**  

**Related Pages：**
- [[concepts/...]]
- [[sources/...]]
```

---

## FAQ Rules

* 8–15 questions
* Must include:

  * beginner questions
  * cross-page synthesis question
* No hallucinated questions

---

# 🧪 Operation: Lint

Detect:

* contradictions
* stale info
* orphan pages
* missing pages
* duplicate concepts
* no-source pages
* outdated pages (>30 days)

Output → `wiki/lint/`

When you **add or materially change** persisted lint artifacts under `wiki/lint/`, update `wiki/index.md` (**Overview** section: link + one-line description) if the catalog should surface them (e.g. link a lint summary page).

Append `wiki/log.md` for **every** Lint run (including when no new files were written — record pass / short summary).

---

# 🧠 Operation: Graph

Build knowledge relationships:

1. Traverse all pages
2. Extract links
3. Infer relationships
4. Generate graph summary
5. When you add or materially change persisted graph artifacts, update `wiki/index.md` (**Overview** section: link + one-line description) (e.g. link `wiki/graph/knowledge-map.md` or the chosen output)
6. Append `wiki/log.md` — do this for every Graph run, including when output is optional or unchanged (record pass / no-op)

Optional output:

```md
wiki/graph/knowledge-map.md
```

---

# 🪵 Logging Rules

Append only:

```md
## [YYYY-MM-DD] <operation> | <title>
```

---

# 🚫 Hard Constraints

* **Do not modify** existing files under `raw/` (immutable). **New** archives into `raw/sources/` as step 2 of Ingest are allowed.
* NEVER hallucinate without marking
* ALWAYS cite
* ALWAYS link pages
* ALWAYS append `wiki/log.md` when completing any operation defined in this document (each run leaves a trace; use pass / no-op when that operation allows no file changes)
* Update `wiki/index.md` when the operation **creates, deletes, or materially changes** wiki pages or catalog-listed artifacts; when an operation’s steps are narrower (e.g. Graph: index only after graph artifacts change), **follow those steps**

---

# 🧠 Behavior Principles

* Conservative > creative
* Explicit > implicit
* Linked > isolated
* Structured > verbose

---

# 📋 Operations Prompts (Copy-Paste)

Canonical English prompts for Ingest / Query / Lint / FAQ / Graph agents. Logging: every run of an operation defined in this document must append `wiki/log.md` (use **pass** or **no-op** when no files changed). Update `wiki/index.md` when the operation creates, deletes, or materially changes wiki pages or catalog-listed artifacts (narrower rules per operation above).

---

## Ingest Prompt

Use this repository as a source-grounded wiki system.

Follow this document (`AGENTS.md`) strictly:
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
1. Check `wiki/` summary pages first (`faq`, `concepts`, `entities`, `queries`).
2. If summary information is sufficient and non-conflicting, answer directly.
3. If summary information is insufficient, ambiguous, or conflicting, verify with `raw/sources/*`.
4. Final answers must include traceable locations (at minimum file paths; include section/line anchors when needed).
5. Cite sources and mark uncertainty (`（確定）`, `（推測）`, `（未知）`) when applicable.
6. If the answer is reusable, persist a new or updated page under `wiki/queries/*` and update `wiki/index.md` (**Queries** section: link + one-line description).
7. **Always** append `wiki/log.md` for this run — including answer-only sessions with no persistence (record **pass** or **no-op** per **Wiki log append** below).

---

## Lint Prompt

Run a wiki quality lint pass and report findings with evidence.

Follow **Operation: Lint** above.

Check for:
- contradictions
- stale information
- orphan pages
- missing pages
- duplicate concepts
- pages without sources
- outdated pages

Output results to `wiki/lint/` and include actionable fixes with file-level references. When you add or materially change persisted lint artifacts under `wiki/lint/`, update `wiki/index.md` (**Overview** section: link + one-line description) if the catalog should surface them.

**Always** append `wiki/log.md` for this run (even if no new lint files were written): one line summary, e.g. `pass` or `no issues` or short findings.

---

## FAQ Prompt

Generate reusable FAQ knowledge from the existing wiki.

Follow **Operation: FAQ** and **FAQ Page Format** / **FAQ Rules** above.

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

Follow **Operation: Graph** above.

1. Traverse wiki pages (respect link and relationship rules in this document).
2. Extract links and infer relationships where appropriate.
3. Generate or update a graph summary (optional artifact example: `wiki/graph/knowledge-map.md`).
4. If you add or materially change persisted graph artifacts, update `wiki/index.md` (**Overview** section: link + one-line description) to link them (e.g. knowledge map).
5. **Always** append `wiki/log.md` for this run — including when output is optional or **unchanged** (record `pass`, `no-op`, or one-line summary).

---

## Wiki log append (pass / no-op)

Use after any operation in this document when file edits were unnecessary but a trace is still required (e.g. Lint/Graph pass with no new artifacts).

1. Append a new dated section to `wiki/log.md` using the format: `## [YYYY-MM-DD] <operation> | <title>`.
2. One or two bullets: state **pass**, **no-op**, or brief outcome; name the operation (lint / graph / faq / ingest / query persist / etc.).
3. Do not rewrite or delete prior log sections.

---

# ⚡ Example Commands

```md
- Ingest: specified path → archive to raw/sources/*.md → wiki (per Ingest steps; use Ingest Prompt above)
- Ingest all files already under raw/sources/ (one pass each; update index + log)
- Generate FAQ from current wiki (8–15 questions, no fabricated Qs; use FAQ Prompt above)
- Answer: <question> with citations and uncertainty markers (use Query Prompt above)
- Lint the wiki (use Lint Prompt above)
- Build knowledge graph (e.g. wiki/graph/knowledge-map.md; use Graph Prompt above)
```
