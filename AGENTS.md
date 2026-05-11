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

* `wiki/`: LLM-managed knowledge base

* `wiki/index.md`: canonical catalog

* `wiki/log.md`: append-only log

* `wiki/sources/`: parsed source knowledge

* `wiki/concepts/`: abstract ideas (MVC, API, Transaction)

* `wiki/entities/`: concrete systems (Vue, Spring Boot, JDBC)

* `wiki/queries/`: reusable Q&A knowledge

* `wiki/faq/`: structured FAQ pages

* `wiki/lint/`: diagnostics

* `wiki/graph/`: relationship mappings (optional advanced)

* `docs/` (**supporting files**, not part of the wiki knowledge corpus):

  * `docs/templates/page-template.md` — index of templates; choose **page-template-source.md** for `wiki/sources/*` or **page-template-concept.md** for other wiki types. MUST still match **Required Frontmatter** below and, for `wiki/sources/*`, the **Source Page Schema** section headings exactly.

  * `docs/OPERATIONS.md` — canonical **copy-paste English prompts** and numbered procedural checklists for Ingest / Query / Lint / FAQ / Graph agents; maintain prompts here as the single source of truth.

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

Starter layouts: **`docs/templates/page-template-source.md`** (`wiki/sources/*`); **`docs/templates/page-template-concept.md`** (concept / entity / query / lint). See **`docs/templates/page-template.md`** for the index.

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

* **`## Overview`**: Short orientation only (scope, how to use this wiki, pointers to repo-root **`AGENTS.md`** and **`wiki/README.md`** when present). Use a few bullets; do not duplicate the full taxonomy—**Concepts** onward hold the linked catalog.
* **`## Concepts` … `## FAQ`**: Each entry = **link + one-line description** (per section).

---

# 🛠 Operation: Ingest

1. Read the **specified** source file (path or artifact provided for this ingest).
2. **Archive** it into `raw/sources/*.md` (new file only; stable name per team convention). **Do not** overwrite or in-place edit existing files under `raw/` unless explicitly approved.
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
6. Persist if reusable
7. Update index + log

## Query Resolution Rule (MANDATORY)

1. Check `wiki/` summary pages first (`faq`, `concepts`, `entities`).
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

When you **add or materially change** persisted lint artifacts under `wiki/lint/`, update `wiki/index.md` if the catalog should surface them (e.g. link a lint summary page).

Append `wiki/log.md` for **every** Lint run (including when no new files were written — record pass / short summary).

---

# 🧠 Operation: Graph

Build knowledge relationships:

1. Traverse all pages
2. Extract links
3. Infer relationships
4. Generate graph summary
5. When you add or materially change persisted graph artifacts, update `wiki/index.md` (e.g. link `wiki/graph/knowledge-map.md` or the chosen output)
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

# ⚡ Example Commands

```md
- Ingest: specified path → archive to raw/sources/*.md → wiki (per Ingest steps)
- Ingest all files already under raw/sources/ (one pass each; update index + log)
- Generate FAQ from current wiki (8–15 questions, no fabricated Qs)
- Answer: <question> with citations and uncertainty markers
- Lint the wiki
- Build knowledge graph (e.g. wiki/graph/knowledge-map.md)
- Copy-paste agent prompts from docs/OPERATIONS.md
```
