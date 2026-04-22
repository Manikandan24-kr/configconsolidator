# Config Consolidator — Approach Document & Milestone Plan
**Prepared for:** Kriyadocs Leadership
**Version:** 1.0 | April 2026
**Scope:** Module 1 — Configuration Consolidator (Focused Build)

---

## 1. Problem Statement

The Kriyadocs onboarding team manually reads through publisher style guide PDFs,
extracts every applicable editorial rule, organises them by category, and builds
a structured Excel sheet that becomes the configuration baseline for that customer.
For a publisher like AAAS this means ~1,700 rules across 17 documents — a process
that takes weeks of senior editorial time per customer.

This effort is high-effort, hard to scale, and largely repeatable. The same
categories of rules appear across every publisher. The same judgement calls get
made manually each time.

**The goal of the Config Consolidator is to automate the extraction and
organisation of these rules, and give the internal team a tool to review,
confirm, and export them — replacing the manual Excel-building process.**

---

## 2. What We Are Building (Focused Scope)

A web-based internal tool where:

1. An onboarding team member creates a session for a new customer
2. Uploads the publisher's style guide PDFs
3. The system extracts all pre-editing rules, organised by category
4. The team member reviews each rule and marks it as **Configure** or **Skip**
5. Rules can be edited inline or new rules added manually
6. The confirmed ruleset is exported as **Excel** and **JSON**

The Excel output matches the structure the team already produces manually today.
The JSON output is the machine-readable ruleset that feeds downstream into
Kriyadocs configuration.

**What this is NOT (in this phase):**
- Not a Quality Checker
- Not a Kriyadocs auto-configurator
- Not customer-facing
- Not a journal-specific differentiator (all rules treated uniformly for now)

---

## 3. Why This Approach

### 3.1 The core insight

The manual process is not difficult because rules are hard to understand.
It is difficult because there are hundreds of them, spread across many PDFs,
written in paragraph prose, with no consistent structure. The team has to
read everything and translate prose into actionable instructions.

An LLM is well-suited to this translation task — reading unstructured prose
and returning structured, categorised, actionable rules — as long as the
extraction is guided tightly by category.

### 3.2 Two-pass extraction (why it matters)

The current POC uses a single extraction pass across all PDF content and
returns 1,200+ fragmented rules. The manual AAAS sheet has ~1,700 clean,
actionable rows. The gap is not volume — it is **quality and structure**.

The new approach uses two extraction passes per PDF:

**Pass 1 — Categorisation**
The LLM reads a section of the PDF and determines which editorial categories
it contains (Abstract rules, Acronyms, Capitalization, Hyphenation, Numbers,
Punctuation, References, Spelling, Statistical Terms, Trademarks, Units,
Figures, General Style). This gives the system a map of which categories
each PDF contributes to.

**Pass 2 — Targeted extraction**
For each category identified in Pass 1, the LLM is sent only the relevant
content with a focused prompt: *"Extract only actionable pre-editing
instructions for [category], one rule per row, as a copyeditor would apply
them."* This produces clean, non-duplicated, properly scoped rules.

This two-pass approach produces output that is structurally comparable to
what the team currently builds manually — the right level of granularity,
no noise, no duplication.

### 3.3 Human stays in the loop

The tool does not auto-approve anything. Every extracted rule starts as
**Pending**. The reviewer makes the final call on every rule. This is
intentional — the tool handles the volume problem, the human handles
the judgement problem.

---

## 4. System Architecture (Overview)

```
┌─────────────────────────────────────────────────┐
│                  FRONTEND (React)                │
│                                                 │
│  Sessions List → Upload → Extraction Progress   │
│       → Review Table → Export                  │
└──────────────────────┬──────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────┐
│               BACKEND (FastAPI / Python)         │
│                                                 │
│  PDF Parser → Two-Pass Extractor → Rule Store   │
│  Session Manager → Export Generator             │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│              DATA LAYER (SQLite → PostgreSQL)    │
│                                                 │
│  customers | sessions | rules | audit_log       │
└─────────────────────────────────────────────────┘
```

**Stack:**
- Frontend: React + Vite (existing, extending)
- Backend: FastAPI Python (existing, extending)
- LLM: OpenAI GPT-4.1-mini (existing) → Claude API (recommended upgrade)
- Database: SQLite for development, PostgreSQL for production
- Export: openpyxl (Excel), native JSON

---

## 5. Data Model

Each rule in the system has the following fields:

| Field | Description |
|---|---|
| `rule_id` | Auto-generated unique ID |
| `session_id` | Customer session this rule belongs to |
| `category` | Abstract / Acronyms / Capitalization / Hyphenation / Numbers / Punctuation / References / Spelling / Statistical Terms / Trademarks / Units / Figures / General Style |
| `rule` | The actionable pre-editing instruction (one sentence) |
| `source_document` | Which PDF this was extracted from |
| `source_section` | Which section within that PDF |
| `status` | `pending` / `confirmed` / `excluded` |
| `is_custom` | `true` if manually added by reviewer |
| `created_at` | Timestamp |
| `updated_at` | Timestamp of last edit |

---

## 6. User Journey (Step by Step)

### Step 1 — Create Customer Session
Team member opens the tool, clicks **+ New Customer**, enters the customer name
(e.g. "Nature Publishing Group"), and creates the session.

### Step 2 — Upload Style Guides
Drags and drops one or more style guide PDFs. Confirms upload.

### Step 3 — Extraction Runs
System shows per-PDF progress. Each PDF goes through two-pass extraction.
On completion, the review screen opens automatically.

### Step 4 — Review Rules
Category sidebar shows all categories with a **confirmed / total** counter.
The main panel shows all rules for the selected category in a table.

Each rule row has:
- The rule statement
- Source document reference
- **Confirm** / **Exclude** / **Edit** actions
- Status badge (Pending / Confirmed / Excluded)

Bulk actions available per category: Confirm All / Exclude All.

### Step 5 — Edit or Add Rules
Clicking **Edit** opens an inline panel to modify any rule.
**+ Add Rule** opens a form to write a custom rule for any category.
Custom rules are tagged with a "Custom" badge.

### Step 6 — Export
Click **Export** and choose:
- **Excel** — one sheet per category, confirmed rules only,
  matching the structure of the existing manual AAAS sheet
- **JSON** — full structured ruleset keyed by category,
  ready for downstream Kriyadocs configuration

Session is always saved and resumable.

---

## 7. Export Format

### Excel Output (matches existing manual sheet structure)
Each sheet = one category (Abstract, Acronyms, Capitalization, etc.)

| Column | Content |
|---|---|
| Requirement | The rule statement |
| Remarks | Internal notes (if any) |
| Source | PDF file and section |
| Status | Confirmed / Custom |

### JSON Output (machine-readable ruleset)
```json
{
  "customer": "AAAS",
  "generated": "2026-04-22",
  "total_confirmed_rules": 312,
  "categories": {
    "abstract": [
      {
        "rule_id": "abstract.001",
        "rule": "Do not cite references in the abstract.",
        "source": "Abstract.2023.pdf — Section: Abstract",
        "status": "confirmed",
        "is_custom": false
      }
    ],
    "capitalization": [ ... ],
    "hyphenation": [ ... ]
  }
}
```

---

## 8. Milestone Plan

### Milestone 1 — Foundation & Data Layer
**Target: Week 1–2**

- [ ] Define and create SQLite schema (customers, sessions, rules, audit_log)
- [ ] Build session management API (create, list, get, delete)
- [ ] Build rules API (list by session/category, update status, add custom, edit)
- [ ] Migrate existing POC in-memory stores to persistent DB
- [ ] Basic session list UI (customer name, date, rule counts, resume button)

**Exit criteria:** A session can be created, rules stored, and retrieved after
browser refresh.

---

### Milestone 2 — Two-Pass Extraction Engine
**Target: Week 2–4**

- [ ] Build Pass 1 prompt — categorisation of PDF section content
- [ ] Build Pass 2 prompts — one focused extraction prompt per category
  (13 category prompts: Abstract, Acronyms, Capitalization, Hyphenation,
  Numbers, Punctuation, References, Spelling, Statistical Terms,
  Trademarks, Units, Figures, General Style)
- [ ] Integrate two-pass pipeline into the processing background task
- [ ] Deduplication logic — remove near-duplicate rules before storing
- [ ] Per-PDF, per-category progress tracking API
- [ ] Test against AAAS PDFs — validate output quality vs. manual sheet

**Exit criteria:** Processing the 17 AAAS PDFs produces clean, categorised
rules that are structurally comparable to the manually built AAAS sheet.
Target: <300 rules per category, no obvious duplicates.

---

### Milestone 3 — Review UI
**Target: Week 4–6**

- [ ] Category sidebar with confirmed/total counters per category
- [ ] Rule table with Confirm / Exclude / Edit per row
- [ ] Status filter (All / Pending / Confirmed / Excluded)
- [ ] Bulk Confirm All / Exclude All per category
- [ ] Inline edit panel (edit rule text, remarks, source)
- [ ] Add Rule form (category, rule text, marks as custom)
- [ ] Custom rule badge in table
- [ ] Session header showing customer name, total progress, last updated

**Exit criteria:** A reviewer can go through all extracted rules, confirm or
exclude each one, add custom rules, and the state persists across sessions.

---

### Milestone 4 — Export
**Target: Week 6–7**

- [ ] Excel export — confirmed rules only, one sheet per category,
  matching manual AAAS sheet column structure
- [ ] JSON export — structured ruleset by category
- [ ] Export options: confirmed only vs. all with status column
- [ ] Download from the UI (single button, format selector)

**Exit criteria:** The exported Excel file is directly usable by the
onboarding team — same structure, same columns as the file they currently
build manually. JSON is valid and parseable.

---

### Milestone 5 — Quality, Hardening & Internal Pilot
**Target: Week 7–9**

- [ ] Error handling — failed PDF parsing, LLM timeouts, partial extractions
- [ ] Re-extraction option — reprocess a single PDF without losing reviewed rules
- [ ] Audit log — track who confirmed/excluded/edited what and when
- [ ] Session duplication — copy a confirmed ruleset as a starting point
  for a similar customer
- [ ] Performance — handle large PDFs (50+ pages) without timeout
- [ ] Internal pilot: run the tool on 2–3 real customer style guides,
  compare output quality against manually built sheets
- [ ] Feedback collected from onboarding team, iteration

**Exit criteria:** Tool used end-to-end by the onboarding team on a real
customer. Team confirms the output is usable and time saving is measurable.

---

### Milestone 6 — Production Readiness
**Target: Week 9–10**

- [ ] Migrate from SQLite to PostgreSQL
- [ ] Authentication (basic login for internal use)
- [ ] Deploy to production environment (Docker)
- [ ] Push to production branch in GitHub
- [ ] Handover documentation for the onboarding team

**Exit criteria:** Tool running in production, onboarding team using it
for new customers independently.

---

## 9. Timeline Summary

| Milestone | Description | Weeks |
|---|---|---|
| M1 | Foundation & Data Layer | 1–2 |
| M2 | Two-Pass Extraction Engine | 2–4 |
| M3 | Review UI | 4–6 |
| M4 | Export (Excel + JSON) | 6–7 |
| M5 | Quality, Hardening & Internal Pilot | 7–9 |
| M6 | Production Readiness | 9–10 |

**Total: 10 weeks to production-ready tool**

---

## 10. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Extraction quality inconsistent across PDF formats | Medium | Two-pass approach + category-specific prompts. Manual add/edit as fallback. |
| LLM produces duplicate or vague rules | Medium | Deduplication pass after extraction. Reviewer catches remainder. |
| Reviewer fatigue on large rulesets (1000+ rules) | Medium | Bulk confirm/exclude per category. Quality extraction reduces noise upfront. |
| LLM API cost at scale | Low | Cache extraction results per document. Re-use cached output if PDF unchanged. |
| PDF parsing fails on complex layouts | Low | Multiple parsing backends (pdfplumber + PyMuPDF). Manual rule entry as fallback. |

---

## 11. Success Metrics

| Metric | Target |
|---|---|
| Time to extract rules from a full style guide | < 30 minutes per customer |
| Extraction quality (rules matching manual sheet) | > 80% of manual sheet rules captured automatically |
| Reviewer time to confirm/exclude/edit full ruleset | < 4 hours per customer |
| Total onboarding time reduction (rule extraction phase) | From ~5 days to < 1 day |
| Excel output usability (team can use without reformatting) | Yes, directly usable |

---

## 12. Future Phases (Out of Scope for This Build)

- **Journal-specific rule tagging** — mark rules as applicable to specific
  sub-journals (Science Advances, Science Immunology, etc.)
- **Handling type tagging** — Pre-editing / Copy-editing / Only in PDF per rule
- **Module 2: Kriyadocs Auto-Configurator** — take the confirmed JSON ruleset
  and auto-configure Kriyadocs platform settings
- **Module 3: Quality Checker** — validate manuscripts against the confirmed
  ruleset with confidence scoring
- **Reverse-engineering from published articles** — infer rules when no
  formal style guide exists
