# KriyaDocs AI Onboarding Platform — Proof of Concept

> Converting the onboarding process into a Strategic Consulting Opportunity.
> Turning ambiguity into alignment — before it costs you.

## What This POC Demonstrates

This is a working proof-of-concept that takes the 17 Science/AAAS style guide PDFs in this folder and turns them into **four tangible deliverables**:

| # | Deliverable | Module | Status |
|---|-------------|--------|--------|
| 1 | **Codified Rule Set** (Sign-Off Document) | Configuration Consolidator | Working |
| 2 | **Compliance Detector** (Audit Tool) | Quality Checker | Working |
| 3 | **RAG Knowledge Agent** (AI Tool) | Knowledge Agent | Working |
| 4 | **Risk & Opportunity Assessment** (Strategy Report) | Discrepancy Analysis | Working |

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key (optional — demo works from cache without one)

### Setup (one time)

```bash
# 1. Install Python dependencies
cd poc/backend
pip3 install -r requirements.txt

# 2. (Optional) Set your API key — not needed if cache/ is pre-populated
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 3. Install frontend dependencies
cd ../frontend
npm install
```

### Cache Mode (Recommended for Demos)
The project ships with pre-cached AI results. No API key is needed for demos.
The backend automatically detects the cache and serves results with simulated
processing delays. To regenerate the cache with fresh AI calls, delete the
`poc/backend/cache/` directory and set an `OPENAI_API_KEY` in the `.env` file.

### Run

```bash
# Option A: Use the startup script
cd poc
./start.sh

# Option B: Start manually (two terminals)
# Terminal 1 — Backend:
cd poc/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 — Frontend:
cd poc/frontend
npx vite --port 3000
```

Then open **http://localhost:3000**

## Demo Walkthrough

### 1. Configuration Consolidator
- Click "Configuration Consolidator" in the top nav
- Click "Load Science/AAAS Demo" (or upload your own PDFs)
- Watch as the system extracts rules from all 17 documents
- See the structured rule set organized by category
- Review the discrepancy report (conflicts, ambiguities, gaps)

### 2. Quality Checker
- Click "Quality Checker" in the top nav
- Click "Load Sample Manuscript" (a realistic CRISPR paper with intentional issues)
- Click "Run Quality Check"
- See issues with confidence scores:
  - **Definitive (95-100%)**: British spellings, abstract word count, title length
  - **High (80-94%)**: Prohibited terms ("novel", "unique"), reference format
  - **Moderate (50-79%)**: Tense issues, wordiness, clarity
  - **Cannot check**: Items explicitly flagged for human review

### 3. Knowledge Agent
- After processing style guides via the Consolidator, go to Knowledge Agent
- Ask natural language questions like:
  - "How should we format references for journal articles?"
  - "What are the rules for acronyms in the abstract?"
  - "When should we use active vs. passive voice?"

## Architecture

```
Frontend (React + Vite, port 3000)
    │
    ├── /api/consolidator/* → PDF parsing + AI rule extraction + conflict detection
    ├── /api/qc/*           → Deterministic + AI quality checks with confidence scores
    └── /api/knowledge/*    → RAG-style Q&A over extracted rules
    │
Backend (FastAPI, port 8001)
    │
    ├── pdf_parser.py       → PDF text extraction with section detection
    ├── rule_extractor.py   → AI-powered rule extraction + conflict analysis (OpenAI GPT-4.1-mini)
    ├── quality_checker.py  → Hybrid deterministic + AI quality checking
    ├── llm_cache.py        → LLM abstraction + file-based caching layer
    └── main.py             → API endpoints and orchestration
```

## What Makes This Convincing

1. **Real data**: Processes the actual Science/AAAS style guide PDFs
2. **Confidence transparency**: Explicitly says what it can and cannot check
3. **Professional output**: The UI matches the KriyaDocs strategic vision (see KriyaDocs_v3.pptx)
4. **Hybrid approach**: Deterministic checks for clear-cut rules, AI for nuanced ones
5. **Traceable**: Every rule links back to its source document and section
6. **Actionable**: Discrepancy reports include specific recommendations

## File Structure

```
poc/
├── start.sh                  # One-click startup
├── README.md                 # This file
├── backend/
│   ├── main.py               # FastAPI application
│   ├── pdf_parser.py         # PDF ingestion pipeline
│   ├── rule_extractor.py     # AI rule extraction (OpenAI GPT-4.1-mini)
│   ├── quality_checker.py    # QC engine with confidence scoring
│   ├── llm_cache.py          # LLM abstraction + caching layer
│   ├── cache/                # Pre-populated AI response cache
│   ├── sample_manuscript.py  # Demo manuscript with intentional issues
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # API key (optional)
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx           # Full application UI
        └── index.css         # Styles
```
