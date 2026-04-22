# Config Consolidator — Sprint Plan
**Active Branch:** dev
**Status:** Sprint 1 starting

---

## Architecture at a Glance

```
PDFs → Two-Pass Extraction → SQLite DB → Review UI → Export (Excel + JSON)
```

**Stack:** FastAPI (Python) + React 18 + Vite + SQLite → PostgreSQL  
**LLM:** OpenAI GPT-4.1-mini via existing cache layer  
**Ports:** Frontend :3000 → proxied to Backend :8001

---

## What We Are Keeping from the POC
| File | Decision |
|---|---|
| pdf_parser.py | Keep as-is |
| llm_cache.py | Keep as-is |
| quality_checker.py | Keep as-is (future module) |
| local_extractor.py | Keep as fallback |
| rule_extractor.py | Keep as fallback |
| index.css | Keep, extend |
| vite.config.js | Keep as-is |

## What We Are Replacing
| Old | New |
|---|---|
| In-memory dicts (jobs, extracted_rules_store) | SQLite via SQLAlchemy |
| Single-pass rule extraction | Two-pass focused extraction pipeline |
| Consolidator UI in App.jsx (monolith) | Componentised React (SessionList → Upload → Progress → Review) |
| Frontend Excel export (xlsx lib) | Backend openpyxl export |

---

## Sprint 1 — Foundation & Extraction Engine
**Goal:** Persistent data layer + two-pass extraction pipeline working end-to-end. Backend only, no UI changes.

### 1.1 — Database Layer
- [ ] `backend/database.py` — SQLite engine, `create_tables()`, `get_db()` dependency
- [ ] `backend/models.py` — SQLAlchemy models: Customer, Session, UploadedFile, Rule, AuditLog
- [ ] Update `requirements.txt` — add `sqlalchemy`, `aiosqlite`, `openpyxl`

**Schema summary:**
```
customers       (id, name, created_at)
sessions        (id, customer_id, name, status, total_rules, confirmed_rules, excluded_rules)
uploaded_files  (id, session_id, filename, filepath, status)
rules           (id, session_id, category, rule, source_document, source_section,
                 remarks, status[pending|confirmed|excluded], is_custom, sort_order)
audit_log       (id, session_id, rule_id, action, old_value, new_value, created_at)
```

### 1.2 — Two-Pass Extraction Engine
- [ ] `backend/extractor/__init__.py`
- [ ] `backend/extractor/pass1_categorise.py` — LLM prompt to map section text → category list
- [ ] `backend/extractor/pass2_extract.py` — 13 focused category extraction prompts
- [ ] `backend/extractor/dedup.py` — Jaccard similarity dedup within each category
- [ ] `backend/extractor/pipeline.py` — Orchestrator: PDF → Pass1 → Pass2 → Dedup → Save to DB

**Two-pass flow:**
```
For each PDF section:
  Pass 1 → ["hyphenation", "punctuation"]
  For each category:
    Pass 2 → [{rule, source_section, remarks}, ...]
    → Save to rules table (status=pending)
After all PDFs:
  Dedup within each category
  session.status = "review"
```

### 1.3 — New API Endpoints (main.py rewrite for consolidator routes)
- [ ] `POST   /api/sessions` — create session
- [ ] `GET    /api/sessions` — list all sessions
- [ ] `GET    /api/sessions/{id}` — get session with category breakdown
- [ ] `DELETE /api/sessions/{id}` — delete session
- [ ] `POST   /api/sessions/{id}/upload` — upload PDFs
- [ ] `POST   /api/sessions/{id}/extract` — start two-pass extraction (background)
- [ ] `GET    /api/sessions/{id}/status` — poll extraction progress
- [ ] `GET    /api/sessions/{id}/rules` — list rules (filter by category/status)
- [ ] `PATCH  /api/rules/{rule_id}` — update status / text / remarks
- [ ] `POST   /api/sessions/{id}/rules` — add custom rule
- [ ] `DELETE /api/rules/{rule_id}` — delete custom rule only
- [ ] `POST   /api/sessions/{id}/rules/bulk` — bulk confirm/exclude by category
- [ ] `GET    /api/sessions/{id}/audit` — audit log

### 1.4 — Sprint 1 Validation
- [ ] Run pipeline on all 17 AAAS PDFs
- [ ] Compare output against `AAAS_Sg/AAAS styleguide.xlsx` (gold standard)
- [ ] Confirm: clean rules, right categories, no obvious duplicates
- [ ] Confirm: rules survive backend restart (DB persistence)

**Exit criteria:** Upload 17 PDFs → extraction runs → rules in DB → retrievable via API. No data loss on restart.

---

## Sprint 2 — Review UI
**Goal:** Complete human-in-the-loop review interface. All rule actions working end-to-end.

### 2.1 — App.jsx Restructure
- [ ] Extract Consolidator tab into own component tree
- [ ] 4 sub-views: `sessions` | `upload` | `extracting` | `review`
- [ ] Keep QC, Knowledge Agent, Home tabs untouched

### 2.2 — Session Management Views
- [ ] `SessionList` — table of all sessions, + New Customer button, Resume
- [ ] `NewSessionModal` — customer name input → POST /api/sessions
- [ ] `UploadZone` — drag-drop PDFs → upload → trigger extraction → navigate to progress

### 2.3 — Extraction Progress View
- [ ] `ExtractionProgress` — polls `/api/sessions/{id}/status` every 2s
- [ ] Per-file status rows (Queued / Extracting / Done)
- [ ] Current category being extracted
- [ ] Rules found so far counter
- [ ] Auto-navigates to review when status = "review"

### 2.4 — Review Interface
- [ ] `ReviewLayout` — two-column layout (sidebar + rule panel)
- [ ] `CategorySidebar` — 13 categories, confirmed/total counter, colour state (grey/blue/green)
- [ ] `ReviewHeader` — customer name, overall progress %, Export button
- [ ] `RuleTableHeader` — filter tabs (All/Pending/Confirmed/Excluded), Confirm All, Exclude All, + Add Rule
- [ ] `RuleTable` + `RuleRow` — rule text, source pill, status badge, action buttons
- [ ] Optimistic updates on confirm/exclude (instant UI, async API)
- [ ] Excluded rows greyed out with Undo button
- [ ] `EditRulePanel` — slide-in from right, handles both edit and add custom rule

### 2.5 — CSS
- [ ] Category sidebar styles
- [ ] Rule row styles (pending / confirmed / excluded states)
- [ ] Status badges
- [ ] EditRulePanel slide-in animation
- [ ] Session list table styles

**Exit criteria:** Full review workflow functional. State persists across refresh. Can confirm, exclude, edit, add rules.

---

## Sprint 3 — Export + Hardening
**Goal:** Excel and JSON export. Error handling. Internal pilot on real customers.

### 3.1 — Export (Backend)
- [ ] `GET /api/sessions/{id}/export/excel` — openpyxl, one sheet per category, confirmed only (default)
- [ ] `GET /api/sessions/{id}/export/json` — structured JSON by category
- [ ] Excel format matches `AAAS styleguide.xlsx` column structure
- [ ] Export options: confirmed only vs. all with status column

### 3.2 — Export (Frontend)
- [ ] Export button in ReviewHeader
- [ ] Dropdown: Excel (Confirmed) | Excel (All) | JSON
- [ ] Trigger download from API response

### 3.3 — Robustness
- [ ] Failed PDF handling (scanned, complex layout, password protected) — flag + allow manual rule entry
- [ ] LLM timeout + retry (3 attempts, then fallback to local extractor for that section)
- [ ] Re-extraction: reprocess one PDF without losing reviewed rules in other categories
- [ ] Session duplication: copy confirmed rules as starting point for new session
- [ ] Progress recovery: if extraction crashes midway, resume from last completed PDF

### 3.4 — Internal Pilot
- [ ] Run tool on 2–3 real customer style guides beyond AAAS
- [ ] Onboarding team uses it in actual workflow
- [ ] Measure: % of manual rules captured automatically, reviewer time vs. manual build
- [ ] Fix issues surfaced during pilot

**Exit criteria:** Excel output directly usable. Tool survives real customer PDFs. Onboarding team validates output quality.

---

## Sprint 4 — Production Readiness
**Goal:** Deployed, authenticated, stable.

### 4.1 — Infrastructure
- [ ] Migrate SQLite → PostgreSQL
- [ ] Basic auth (username/password, internal only)
- [ ] Docker: Dockerfile for backend, frontend build served via nginx
- [ ] docker-compose.yml: backend + db + frontend
- [ ] Deploy to Kriyadocs infrastructure

### 4.2 — Monitoring
- [ ] Structured logging (request IDs, session IDs in all log lines)
- [ ] Error alerting for extraction failures

### 4.3 — Handover
- [ ] Team user guide (create session, upload, review, export)
- [ ] Engineering guide (deployment, env vars, DB backup)
- [ ] Push to production branch, both GitHub remotes

---

## File Creation Checklist (new files to be created)

### Backend (new)
```
poc/backend/database.py
poc/backend/models.py
poc/backend/extractor/__init__.py
poc/backend/extractor/pipeline.py
poc/backend/extractor/pass1_categorise.py
poc/backend/extractor/pass2_extract.py
poc/backend/extractor/dedup.py
```

### Backend (modified)
```
poc/backend/main.py          — new consolidator routes, keep QC/knowledge routes
poc/backend/requirements.txt — add sqlalchemy, aiosqlite, openpyxl
```

### Frontend (new)
```
poc/frontend/src/components/consolidator/SessionList.jsx
poc/frontend/src/components/consolidator/NewSessionModal.jsx
poc/frontend/src/components/consolidator/UploadZone.jsx
poc/frontend/src/components/consolidator/ExtractionProgress.jsx
poc/frontend/src/components/consolidator/ReviewLayout.jsx
poc/frontend/src/components/consolidator/CategorySidebar.jsx
poc/frontend/src/components/consolidator/ReviewHeader.jsx
poc/frontend/src/components/consolidator/RuleTableHeader.jsx
poc/frontend/src/components/consolidator/RuleTable.jsx
poc/frontend/src/components/consolidator/RuleRow.jsx
poc/frontend/src/components/consolidator/EditRulePanel.jsx
```

### Frontend (modified)
```
poc/frontend/src/App.jsx     — Consolidator tab rebuilt, other tabs unchanged
poc/frontend/src/index.css   — New component styles added
```

---

## Decision Log (quick reference)
| Decision | Choice |
|---|---|
| DB | SQLite (dev) → PostgreSQL (prod) |
| Extraction | Two-pass: categorise then extract per category |
| Export | Backend openpyxl, not frontend xlsx |
| State mgmt | React useState only, no Redux |
| Excluded rules | Soft delete (status=excluded), never hard delete extracted rules |
| UI updates | Optimistic on confirm/exclude, revert on API error |
| Categories | 13 fixed categories, hardcoded |
| LLM | Keep OpenAI GPT-4.1-mini, Claude upgrade flagged for future |
