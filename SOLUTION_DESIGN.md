# Kriyadocs AI-Powered Onboarding Platform — Solution Design

## Executive Summary

When onboarding a new publisher to Kriyadocs, the team must manually analyze style guides, identify rules, find discrepancies, configure the platform, and set up quality checks. This is slow, error-prone, and doesn't scale.

This document proposes a **three-module AI system** that transforms this from a weeks-long manual process into a guided, semi-automated workflow that produces auditable, customer-signable outputs.

---

## The Three Modules

```
┌─────────────────────────────────────────────────────────────┐
│                    CUSTOMER INPUTS                          │
│  Style guides, published PDFs, email templates, ad-hoc docs │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           MODULE 1: CONFIGURATION CONSOLIDATOR              │
│                                                             │
│  Ingests documents → Extracts rules → Resolves conflicts    │
│  → Produces formatted guideline document for sign-off       │
│                                                             │
│  OUTPUT: Structured ruleset + Discrepancy report            │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌──────────────────┐ ┌──────────┐ ┌──────────────────┐
│  MODULE 2:       │ │          │ │  MODULE 3:       │
│  CONFIGURATOR    │ │  HUMAN   │ │  QUALITY CHECKER │
│                  │ │  SIGN-OFF│ │                  │
│  Auto-configures │ │          │ │  Validates docs  │
│  Kriyadocs from  │ │          │ │  against rules   │
│  the ruleset     │ │          │ │  with confidence │
│                  │ │          │ │  scoring         │
└──────────────────┘ └──────────┘ └──────────────────┘
```

---

## MODULE 1: Configuration Consolidator

### Purpose
Take raw customer documents (style guides, published articles, email templates) and produce a **clean, formatted, auditable guideline document** that the customer can review and sign off on — similar to how Optisol documented the Kriyadocs codebase and returned it.

### Input Types
1. **Formal style guides** (like the Science/AAAS PDFs we have)
2. **Published articles** (when no formal guide exists — reverse-engineer the rules)
3. **Communication templates** (email templates, workflow instructions)
4. **Ad-hoc instructions** (scattered notes, emails, tribal knowledge)

### Processing Pipeline

```
STAGE 1: DOCUMENT INGESTION
├── PDF extraction (text + layout analysis)
├── DOCX/HTML parsing
├── OCR for scanned documents
└── Published article analysis (when no formal guide exists)

STAGE 2: RULE EXTRACTION (AI-powered)
├── Editorial Rules
│   ├── Language & Grammar
│   │   ├── Tense usage (e.g., "past tense for results, present for conclusions")
│   │   ├── Voice preferences (active vs. passive)
│   │   ├── Wordiness/redundancy rules
│   │   ├── Clarity rules (dangling modifiers, freight-train modifiers)
│   │   └── Prohibited phrases ("novel", "unique", "first", "data not shown")
│   ├── Spelling & Terminology
│   │   ├── US vs. British English preferences
│   │   ├── Preferred spellings (e.g., "waveform" not "wave form")
│   │   ├── Scientific nomenclature (genus/species, chemical names)
│   │   └── Trademark handling
│   ├── Punctuation
│   │   ├── Serial comma rules
│   │   ├── Apostrophe rules (possessives, plurals, eponyms)
│   │   ├── Bracket/parentheses usage
│   │   ├── Colon/semicolon rules
│   │   └── Hyphenation rules
│   ├── Numbers & Units
│   │   ├── Spell-out vs. numeral rules
│   │   ├── SI/metric unit preferences
│   │   ├── Statistical notation (P values, confidence intervals)
│   │   └── Mathematical formatting
│   ├── Abbreviations & Acronyms
│   │   ├── First-use expansion rules
│   │   ├── Standard abbreviations list
│   │   └── Context-specific rules (abstract vs. body)
│   └── References & Citations
│       ├── Citation format (numbered, author-year, etc.)
│       ├── Reference formatting (journal, book, web, etc.)
│       ├── Author name formatting
│       ├── Journal abbreviation preferences (MEDLINE vs. ISO)
│       └── Special cases (preprints, "in press", unpublished)
│
├── Typesetting Rules
│   ├── Heading hierarchy (levels, styling, case)
│   ├── Figure/table formatting (legends, panel labels, bold usage)
│   ├── Block quote formatting
│   ├── Font/emphasis rules (when to bold, italicize)
│   ├── Page layout specifications
│   └── Abstract structure and constraints
│
└── Communication/Workflow Guidelines
    ├── Email templates
    ├── Author query templates
    └── Internal process instructions

STAGE 3: CONFLICT DETECTION & DISCREPANCY ANALYSIS
├── Within-document conflicts (Rule A says X, Rule B implies Y)
├── Cross-document conflicts (Style guide says X, published articles show Y)
├── Ambiguity detection (rules that are vague or open to interpretation)
├── Gap analysis (common areas not covered by the guide)
└── Deviation analysis (published files vs. stated rules)

STAGE 4: OUTPUT GENERATION
├── Formatted HTML guideline document (for customer sign-off)
├── Discrepancy report with highlighted areas needing attention
├── Machine-readable ruleset (JSON/YAML) for Module 2 & 3
└── Coverage report (what's documented vs. what's missing)
```

### Key Innovation: Reverse-Engineering from Published Files

When a customer has no formal style guide, the system can:
1. Ingest 10-20 published articles/documents
2. Use AI to identify **consistent patterns** across the corpus
3. Flag **inconsistencies** between articles (these become questions for the customer)
4. Generate a **draft style guide** from observed patterns
5. Present it to the customer: "Based on your published work, here's what we infer your style rules are — please confirm or correct."

### Output Format

The output is an **interactive HTML document** organized by category:

```
┌─────────────────────────────────────────────────────┐
│  PUBLISHER STYLE GUIDE — [Customer Name]            │
│  Generated: [Date] | Status: AWAITING SIGN-OFF      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ⚠ DISCREPANCIES FOUND: 12 items need attention     │
│  [View Discrepancy Report]                          │
│                                                     │
│  ─── EDITORIAL RULES ────────────────────────────   │
│                                                     │
│  1. LANGUAGE & GRAMMAR                              │
│     1.1 Tense Usage                                 │
│         Rule: Use past tense for experimental       │
│         results, present tense for conclusions.     │
│         Source: General Style Guide, p.1            │
│         Confidence: ██████████ HIGH                 │
│         ⚠ Note: 3 published articles use present   │
│           tense for results — confirm preference.   │
│                                                     │
│     1.2 Voice                                       │
│         Rule: Prefer active voice when...           │
│         [...]                                       │
│                                                     │
│  2. SPELLING & TERMINOLOGY                          │
│     [...]                                           │
│                                                     │
│  ─── TYPESETTING RULES ──────────────────────────   │
│     [...]                                           │
│                                                     │
│  ─── COMMUNICATION GUIDELINES ───────────────────   │
│     [...]                                           │
│                                                     │
│  [✓ APPROVE]  [✎ REQUEST CHANGES]  [↓ EXPORT PDF]  │
└─────────────────────────────────────────────────────┘
```

### Machine-Readable Ruleset (feeds into Module 2 & 3)

```json
{
  "publisher": "Science/AAAS",
  "version": "2025.1",
  "categories": {
    "editorial": {
      "language": {
        "tense": {
          "results": "past",
          "conclusions": "present",
          "prior_work": "past_or_past_perfect"
        },
        "voice": {
          "preference": "active",
          "exceptions": ["when emphasis on results, not authors"]
        },
        "prohibited_terms": [
          {"term": "novel", "context": "describing findings", "action": "remove_or_replace", "alternatives": ["previously unidentified", "unexpected"]},
          {"term": "unique", "context": "describing findings", "action": "remove_or_replace"},
          {"term": "for the first time", "context": "claims of priority", "action": "remove"}
        ]
      },
      "spelling": {
        "dialect": "us_english",
        "exceptions": ["author affiliations", "organization names", "journal titles"],
        "preferred_forms": {
          "waveform": {"not": "wave form", "source": "General Style Guide"},
          "Wilms tumor": {"not": "Wilm's tumor", "source": "General Style Guide"}
        }
      },
      "references": {
        "style": "numbered_sequential",
        "author_format": "initials_first_space_separated",
        "max_authors_before_et_al": 5,
        "journal_names": "italic_abbreviated_medline",
        "volume": "boldface",
        "year": "parenthetical"
      }
    },
    "typesetting": {
      "headings": {
        "level_1": {"case": "sentence", "style": "bold"},
        "level_2": {"case": "sentence", "style": "bold_italic"},
        "level_3": {"case": "sentence", "style": "italic"}
      },
      "abstract": {
        "max_words": 125,
        "structure": "background_results_conclusions",
        "restrictions": ["no_references", "no_figures", "no_tables", "spell_out_units"]
      }
    }
  }
}
```

---

## MODULE 2: Configurator

### Purpose
Take the signed-off ruleset from Module 1 and **automatically configure Kriyadocs**, then provide interactive previews so the customer can see exactly how their content will look and flow.

### Sub-modules

#### 2A. Pre-Editing Rules Configurator
Maps editorial rules to Kriyadocs' pre-editing engine.

```
RULESET (from Module 1)              KRIYADOCS CONFIGURATION
─────────────────────                ──────────────────────────
prohibited_terms.novel        →     Find-and-flag rule: "novel" in context
tense.results = past          →     Tense-check rule for Results sections
spelling.dialect = us_english →     Spellcheck dictionary: en-US
acronym.first_use_expand      →     Acronym tracker: flag undefined acronyms
reference.style = numbered    →     Reference formatter: numbered sequential
```

**Preview capability**: Show a sample document with the pre-editing rules applied:
- Original text on the left
- Corrected/flagged text on the right
- Color-coded annotations showing which rule triggered each change
- Similar to "Track Changes" in Word but driven by the configured rules

```
┌──────────────────────────┬──────────────────────────┐
│  ORIGINAL                │  WITH RULES APPLIED      │
├──────────────────────────┼──────────────────────────┤
│ We describe a novel      │ We describe a ███████    │
│ method for DNA           │ method for DNA           │
│ sequencing.              │ sequencing.              │
│                          │ ⚠ "novel" flagged —      │
│                          │   consider "previously   │
│                          │   uncharacterized"       │
│                          │                          │
│ The data shows that      │ The data ████ that       │
│ temperatures increased.  │ temperatures increased.  │
│                          │ ⚠ "shows" → "showed"    │
│                          │   (past tense for        │
│                          │    results)              │
└──────────────────────────┴──────────────────────────┘
```

#### 2B. Typesetting Rules Configurator
Maps typesetting rules to Kriyadocs' layout engine.

**Preview capability**: Generate a PDF preview showing how a sample article will look with the configured typesetting rules:
- Heading styles applied
- Figure/table formatting
- Reference list formatting
- Abstract layout
- Font choices and spacing

#### 2C. Workflow Configurator
Maps process/communication guidelines to Kriyadocs workflows.

**Preview capability**: Interactive workflow demo where the user can:
1. See the workflow stages (submission → pre-edit → typeset → review → publish)
2. Click through each stage
3. See which automated checks run at each gate
4. See sample email notifications that would be sent
5. See the roles and permissions at each stage

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐    ┌─────────┐
│ INGEST  │───▶│ PRE-EDIT │───▶│ TYPESET  │───▶│ REVIEW │───▶│ PUBLISH │
│         │    │          │    │          │    │        │    │         │
│ Upload  │    │ AI rules │    │ Layout   │    │ QC     │    │ Final   │
│ Parse   │    │ applied  │    │ applied  │    │ checks │    │ output  │
│ Validate│    │ Author   │    │ PDF gen  │    │ Author │    │         │
│         │    │ queries  │    │          │    │ proof  │    │         │
└─────────┘    └──────────┘    └──────────┘    └────────┘    └─────────┘
     │              │               │              │              │
     ▼              ▼               ▼              ▼              ▼
  [Click to      [Click to      [Click to     [Click to      [Click to
   see demo]      see demo]      see PDF]      see QC]        see output]
```

### Configuration Mapping Engine

The core engine that translates the JSON ruleset into Kriyadocs-native configurations:

```
Input:  Structured ruleset (JSON from Module 1)
        ↓
Step 1: Rule-to-Feature mapping
        (map each rule to the corresponding Kriyadocs feature/setting)
        ↓
Step 2: Conflict resolution
        (handle cases where rules conflict with platform capabilities)
        ↓
Step 3: Gap identification
        (flag rules that cannot be automated — need manual process)
        ↓
Step 4: Configuration generation
        (produce Kriyadocs-native configuration files/API calls)
        ↓
Step 5: Preview generation
        (render sample outputs using the configuration)
        ↓
Output: Kriyadocs configuration + Preview artifacts + Gap report
```

---

## MODULE 3: Quality Checker

### Purpose
Use the consolidated ruleset to **automatically check documents for compliance**, with explicit confidence scoring — clearly reporting what it could check conclusively vs. what needs human review.

### This IS the "Checks" Project

This module is essentially what the COO has been describing as the "checks project." The key differentiator is the **transparency about confidence levels**.

### Check Categories & Confidence Model

```
CONFIDENCE LEVELS:
━━━━━━━━━━━━━━━━━

██████████  DEFINITIVE (95-100%)
  Rule is unambiguous, check is deterministic.
  Examples:
  - Spelling (US vs. British): "colour" → "color"  ✓ DEFINITIVE
  - Reference format: missing bold volume number    ✓ DEFINITIVE
  - Abstract word count > 125                       ✓ DEFINITIVE
  - Acronym not expanded at first use               ✓ DEFINITIVE
  - Title exceeds 96 characters                     ✓ DEFINITIVE

████████░░  HIGH CONFIDENCE (80-94%)
  Rule is clear, but context matters.
  Examples:
  - "novel" used to describe findings               ✓ HIGH (might be valid for actual inventions)
  - Past tense not used in results section           ✓ HIGH (need to identify section boundaries)
  - Hyphenation of compound modifiers                ✓ HIGH (most cases are clear)

██████░░░░  MODERATE CONFIDENCE (50-79%)
  Rule requires judgment or interpretation.
  Examples:
  - Wordiness detection ("were the first signs that pointed to")
  - Dangling modifier detection
  - "Freight-train" modifier detection
  - Whether a metaphor is appropriate

████░░░░░░  LOW CONFIDENCE (20-49%)
  Rule is subjective or context-dependent.
  Examples:
  - Whether active voice is more appropriate here
  - Whether an adverb should be deleted
  - Whether "very" adds meaning in this context

██░░░░░░░░  CANNOT CHECK (<20%)
  Rule requires deep domain knowledge or human judgment.
  Examples:
  - Whether a dedication is for a deceased person
  - Whether a figure legend adequately describes the figure
  - Whether the abstract structure is "broad intro → specific → results → conclusions"
  - Whether jargon is too discipline-specific
```

### QC Report Output

```
┌─────────────────────────────────────────────────────────────┐
│  QUALITY CHECK REPORT — [Document Title]                    │
│  Checked against: [Publisher] Style Guide v[X]              │
│  Date: [Date]                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SUMMARY                                                    │
│  ────────                                                   │
│  Total rules checked:        247                            │
│  Definitive issues found:     18  ← FIX THESE              │
│  High-confidence issues:      12  ← LIKELY FIX             │
│  Moderate-confidence flags:    8  ← HUMAN REVIEW            │
│  Low-confidence flags:         5  ← OPTIONAL REVIEW         │
│  Rules NOT checkable:         23  ← MANUAL QC NEEDED        │
│                                                             │
│  ═══════════════════════════════════════════════════════     │
│                                                             │
│  DEFINITIVE ISSUES (must fix)                               │
│  ─────────────────────────────                              │
│  ■ Line 42: "behaviour" → "behavior" [US English required]  │
│  ■ Line 87: Reference 12 — volume not in boldface           │
│  ■ Line 3:  Abstract is 142 words (max: 125)                │
│  ■ Line 15: "DNA" not expanded at first use                 │
│  [...]                                                      │
│                                                             │
│  HIGH-CONFIDENCE ISSUES (likely need fixing)                │
│  ──────────────────────────────────────────                  │
│  ▲ Line 28: "novel gene" — consider "previously             │
│    unidentified gene" [Science prohibits "novel"            │
│    for findings; however, check if this is a truly          │
│    new construct]                                           │
│  [...]                                                      │
│                                                             │
│  ITEMS REQUIRING HUMAN REVIEW                               │
│  ────────────────────────────                               │
│  ○ Line 55: Possible dangling modifier — verify             │
│    subject of "Using the same procedure..."                 │
│  ○ Line 73: Consider whether "very precise" adds            │
│    meaning or is redundant here                             │
│  [...]                                                      │
│                                                             │
│  RULES WE COULD NOT CHECK                                   │
│  ─────────────────────────                                  │
│  These require manual QC by a human editor:                 │
│  □ Abstract structure (broad intro → specific → results)    │
│  □ Figure legends adequately describe content               │
│  □ Metaphors and figures of speech are appropriate          │
│  □ Affiliations correspond to where work was done           │
│  □ Dedication is for deceased person only                   │
│  [...]                                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Learning Loop

The Quality Checker improves over time:

```
Document checked → Human editor reviews AI flags →
  ├── AI was right → reinforces rule understanding
  ├── AI was wrong → adjusts confidence threshold
  ├── AI missed something → new rule/pattern added
  └── Human found issue AI couldn't → stays in "manual" category
```

---

## Technical Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         WEB APPLICATION                         │
│                      (React/Next.js Frontend)                   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Consolidator │  │ Configurator │  │   Quality Checker    │  │
│  │     UI       │  │     UI       │  │        UI            │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
└─────────┼─────────────────┼──────────────────────┼──────────────┘
          │                 │                      │
          ▼                 ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                              │
│                    (FastAPI / Node.js)                           │
└─────────┬─────────────────┬──────────────────────┬──────────────┘
          │                 │                      │
          ▼                 ▼                      ▼
┌──────────────────┐ ┌──────────────┐ ┌────────────────────────┐
│   CONSOLIDATOR   │ │ CONFIGURATOR │ │    QUALITY CHECKER     │
│    SERVICE       │ │   SERVICE    │ │      SERVICE           │
│                  │ │              │ │                        │
│ - PDF Parser     │ │ - Rule       │ │ - Rule Engine          │
│ - AI Extractor   │ │   Mapper     │ │ - Confidence Scorer    │
│ - Conflict       │ │ - Preview    │ │ - Report Generator     │
│   Detector       │ │   Generator  │ │ - Learning Loop        │
│ - Report         │ │ - Workflow   │ │                        │
│   Generator      │ │   Builder    │ │                        │
└────────┬─────────┘ └──────┬───────┘ └───────────┬────────────┘
         │                  │                      │
         ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SHARED SERVICES                           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │  LLM Layer   │  │  Document    │  │   Ruleset Store       │ │
│  │  (Claude /   │  │  Storage     │  │   (PostgreSQL +       │ │
│  │   GPT API)   │  │  (S3)       │  │    Vector DB)         │ │
│  └──────────────┘  └──────────────┘  └───────────────────────┘ │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │  PDF         │  │  Kriyadocs   │  │   Audit Log           │ │
│  │  Generator   │  │  Config API  │  │                       │ │
│  │  (WeasyPrint)│  │              │  │                       │ │
│  └──────────────┘  └──────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack (Recommended)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend | React + Next.js | Rich UI for previews, interactive workflow demos |
| API | FastAPI (Python) | LLM integration is Python-native; async support |
| LLM | Claude API (Anthropic) | Best at nuanced language understanding, long context for full style guides |
| PDF Parsing | PyMuPDF + pdfplumber | Handles complex layouts, tables, scientific notation |
| Document Store | PostgreSQL + pgvector | Structured rules + vector search for similar rules |
| File Storage | S3 / MinIO | Customer document storage |
| PDF Generation | WeasyPrint / Puppeteer | Preview PDFs for typesetting rules |
| Task Queue | Celery + Redis | Async processing of large documents |
| Deployment | Docker + Kubernetes | Scalable, matches Kriyadocs infra |

### LLM Usage Strategy

The system uses LLMs strategically — not as a black box:

```
WHAT LLM DOES:                          WHAT DETERMINISTIC CODE DOES:
─────────────────                        ──────────────────────────────
- Extract rules from natural language    - Spelling checks (dictionary-based)
- Understand nuance/exceptions           - Reference format validation (regex)
- Detect conflicts between rules         - Word count checks
- Reverse-engineer rules from articles   - Acronym first-use tracking
- Generate human-readable reports        - Heading level validation
- Classify check confidence levels       - Character count checks
- Handle ambiguous/context-dependent     - Style template matching
  checks                                - Configuration file generation
```

This hybrid approach gives you:
- **Speed**: Deterministic checks are instant
- **Accuracy**: No LLM hallucination for clear-cut rules
- **Nuance**: LLM handles the genuinely ambiguous cases
- **Cost**: LLM only called when needed, not for every check

---

## Implementation Phases

### Phase 1: Configuration Consolidator (MVP) — 8-10 weeks

**Goal**: Given PDFs like the Science style guide, produce a formatted HTML guideline document.

| Week | Deliverable |
|------|-------------|
| 1-2 | PDF ingestion pipeline (extract text, tables, structure from style guide PDFs) |
| 3-4 | AI rule extraction engine (parse rules into structured categories) |
| 5-6 | Conflict detection + discrepancy analysis |
| 7-8 | HTML report generator (formatted output with sign-off capability) |
| 9-10 | Testing with 3-5 real customer style guides, iteration |

**MVP Output**: Upload PDFs → Get formatted HTML guideline document + discrepancy report.

### Phase 2: Quality Checker — 6-8 weeks (can overlap with Phase 1)

**Goal**: Given a document + ruleset, produce a confidence-scored QC report.

| Week | Deliverable |
|------|-------------|
| 1-2 | Deterministic check engine (spelling, reference format, counts, acronyms) |
| 3-4 | LLM-powered checks (prohibited terms, tense, voice, style) |
| 5-6 | Confidence scoring model + report generation |
| 7-8 | Feedback loop (editor corrections improve future checks) |

**MVP Output**: Upload document → Get QC report with confidence-scored issues.

### Phase 3: Configurator — 6-8 weeks

**Goal**: Auto-configure Kriyadocs from the ruleset + provide previews.

| Week | Deliverable |
|------|-------------|
| 1-2 | Rule-to-Kriyadocs feature mapping engine |
| 3-4 | Pre-editing rules preview (side-by-side before/after) |
| 5-6 | Typesetting preview (PDF generation) |
| 7-8 | Workflow demo capability (clickable stage-by-stage walkthrough) |

**MVP Output**: Signed-off ruleset → Kriyadocs configured + visual previews.

### Phase 4: Reverse-Engineering from Published Files — 4-6 weeks

**Goal**: When no formal style guide exists, infer rules from published articles.

| Week | Deliverable |
|------|-------------|
| 1-2 | Multi-document pattern analysis |
| 3-4 | Consistency/inconsistency detection across corpus |
| 5-6 | Draft style guide generation from observed patterns |

---

## How This Changes the Onboarding Workflow

### Current Process (Manual)

```
Customer sends docs (Day 1)
    → Team reads through all docs (Day 2-5)
    → Team writes up instructions (Day 5-10)
    → Back and forth with customer (Day 10-20)
    → Manual Kriyadocs configuration (Day 20-25)
    → Testing and QC setup (Day 25-35)
    → Go live (Day 35+)
```

### New Process (AI-Assisted)

```
Customer sends docs (Day 1)
    → Upload to Consolidator (Day 1, 30 mins)
    → AI produces formatted guideline + discrepancy report (Day 1, ~2 hours processing)
    → Team reviews AI output, makes minor corrections (Day 2-3)
    → Send formatted guide to customer for sign-off (Day 3)
    → Customer reviews, provides feedback (Day 3-7)
    → Configurator auto-configures Kriyadocs (Day 7, ~1 hour)
    → Customer sees previews, approves (Day 7-8)
    → Quality Checker begins validating documents (Day 8+)
    → Go live (Day 10-12)
```

**Estimated time reduction: 35+ days → ~12 days (65% reduction)**

---

## Key Differentiators & Value Propositions

1. **Transparency**: Unlike black-box AI, the system explicitly tells you what it can and cannot check, with confidence scores.

2. **Auditability**: Every extracted rule links back to its source document and page number. Nothing is invented.

3. **Customer-facing output**: The formatted guideline document is professional enough to send directly to customers for sign-off — it IS the deliverable, not just an internal tool.

4. **Feedback loop**: The system gets smarter over time as editors correct its outputs. Each customer onboarded improves the next one.

5. **Scalability**: What currently requires senior editors can be partially offloaded, allowing the team to onboard more customers simultaneously.

6. **Gap honesty**: The system explicitly says "I cannot check these 23 rules — a human editor needs to verify them." This builds trust and ensures nothing falls through the cracks.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM hallucination (inventing rules) | High | Every rule must link to source document + page. Human review before sign-off. |
| PDF parsing failures (complex layouts, tables) | Medium | Multiple parsing backends (PyMuPDF + pdfplumber + OCR fallback). Manual upload option for failed sections. |
| Over-reliance on AI (editors stop checking) | High | System explicitly lists what it CANNOT check. Mandatory human sign-off step. |
| Customer style guides are too vague | Medium | Gap analysis highlights missing areas. Reverse-engineering from published files fills gaps. |
| Kriyadocs config API limitations | Medium | Gap report identifies rules that need manual config. Prioritize most-used features first. |
| LLM cost at scale | Low-Medium | Hybrid approach (deterministic where possible). Cache extracted rulesets. LLM only for new docs. |

---

## Immediate Next Steps

1. **Validate with the Science/AAAS style guides in this folder** — build a proof-of-concept that extracts rules from these 17 PDFs and produces a formatted output.

2. **Map Kriyadocs configuration schema** — document what configurations exist today so Module 2 knows what to target.

3. **Catalog the "checks" project requirements** — align Module 3 with what the COO has already envisioned.

4. **Pick 2-3 additional publishers** with different style guide formats to stress-test the approach.

5. **Decide build vs. integrate** — some components (PDF parsing, spellcheck) have mature OSS solutions; the AI extraction and confidence scoring are the custom IP.
