"""
KriyaDocs AI Onboarding Platform — FastAPI Backend
Serves the Configuration Consolidator, Quality Checker, and Knowledge Agent.
Auto-detects whether an API key is available and falls back to local processing if not.
"""
import os
import json
import re
import uuid
from pathlib import Path
from dataclasses import asdict

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from pdf_parser import extract_pdf, extract_all_pdfs, ExtractedDocument
from quality_checker import run_quality_check, qc_report_to_dict
from sample_manuscript import SAMPLE_MANUSCRIPT

# ── Detect AI availability ────────────────────────────────────────
from llm_cache import is_cache_warm, cache_stats

HAS_API_KEY = bool(os.getenv("OPENAI_API_KEY"))

if HAS_API_KEY:
    from rule_extractor import (
        extract_rules_from_section as ai_extract_rules,
        detect_discrepancies as ai_detect_discrepancies,
        rules_to_dict, discrepancies_to_dict, ExtractedRule
    )
    print("AI mode: OpenAI API key detected — using GPT-4.1-mini for rule extraction.")
elif is_cache_warm():
    from rule_extractor import (
        extract_rules_from_section as ai_extract_rules,
        detect_discrepancies as ai_detect_discrepancies,
        rules_to_dict, discrepancies_to_dict, ExtractedRule
    )
    HAS_API_KEY = True  # Treat warm cache as having AI capability
    print("CACHE mode: No API key, but cache is warm — serving cached AI results.")
else:
    from local_extractor import (
        extract_rules_locally,
        detect_discrepancies_locally,
        rules_to_dict, discrepancies_to_dict, ExtractedRule
    )
    print("LOCAL mode: No API key and no cache — using heuristic rule extraction (no cost, instant).")


app = FastAPI(
    title="KriyaDocs AI Onboarding Platform",
    description="Configuration Consolidator + Quality Checker + Knowledge Agent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory storage for the POC ───────────────────────────────────
UPLOAD_DIR = Path("/tmp/kriyadocs_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

jobs: dict = {}
extracted_rules_store: dict = {}  # session_id -> list of rules
discrepancies_store: dict = {}  # session_id -> list of discrepancies
documents_store: dict = {}  # session_id -> list of extracted docs


class QCRequest(BaseModel):
    text: str
    document_name: str = "Uploaded Document"
    use_ai: bool = True


class KnowledgeQuery(BaseModel):
    question: str
    session_id: str = "default"


# ── Health Check ────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "ai_available": HAS_API_KEY,
        "mode": "openai" if HAS_API_KEY else "local",
        "cache": cache_stats(),
    }


# ── Module 1: Configuration Consolidator ────────────────────────────

@app.post("/api/consolidator/upload")
async def upload_styleguides(files: list[UploadFile] = File(...)):
    """Upload one or more style guide PDFs for processing."""
    session_id = str(uuid.uuid4())[:8]
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    saved_files = []
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            continue
        file_path = session_dir / f.filename
        content = await f.read()
        file_path.write_bytes(content)
        saved_files.append(str(file_path))

    if not saved_files:
        raise HTTPException(400, "No PDF files uploaded")

    jobs[session_id] = {
        "status": "processing",
        "progress": 0,
        "message": f"Uploaded {len(saved_files)} files. Starting extraction...",
        "files": saved_files,
    }

    return {"session_id": session_id, "files_uploaded": len(saved_files)}


@app.post("/api/consolidator/process/{session_id}")
async def process_styleguides(session_id: str, background_tasks: BackgroundTasks):
    """Start processing uploaded style guides (extraction + analysis)."""
    if session_id not in jobs:
        raise HTTPException(404, "Session not found")

    background_tasks.add_task(_process_session, session_id)
    return {"status": "processing", "session_id": session_id}


def _process_session(session_id: str):
    """Background task: extract rules from all uploaded PDFs.
    Automatically uses AI or local extraction based on API key availability."""
    try:
        job = jobs[session_id]
        file_paths = job["files"]
        all_rules = []
        all_docs = []

        total_steps = len(file_paths) + 1
        step = 0
        mode = "AI (GPT-4.1-mini)" if HAS_API_KEY else "local heuristics"

        for fp in file_paths:
            step += 1
            filename = Path(fp).name
            job["progress"] = int((step / total_steps) * 80)
            job["message"] = f"[{mode}] Extracting rules from {filename}..."

            doc = extract_pdf(fp)
            all_docs.append(doc)

            for section in doc.sections:
                if HAS_API_KEY:
                    rules = ai_extract_rules(
                        filename=doc.filename,
                        section_title=section.title,
                        content=section.content,
                    )
                else:
                    rules = extract_rules_locally(
                        filename=doc.filename,
                        section_title=section.title,
                        content=section.content,
                    )
                all_rules.extend(rules)

        # Discrepancy analysis
        job["progress"] = 85
        job["message"] = f"[{mode}] Analyzing for conflicts and discrepancies..."

        if HAS_API_KEY:
            discrepancies = ai_detect_discrepancies(all_rules)
        else:
            discrepancies = detect_discrepancies_locally(all_rules)

        # Store results
        extracted_rules_store[session_id] = all_rules
        discrepancies_store[session_id] = discrepancies
        documents_store[session_id] = all_docs

        job["status"] = "completed"
        job["progress"] = 100
        job["message"] = f"Done! Extracted {len(all_rules)} rules, found {len(discrepancies)} discrepancies. (Mode: {mode})"

    except Exception as e:
        import traceback
        traceback.print_exc()
        jobs[session_id]["status"] = "failed"
        jobs[session_id]["message"] = f"Error: {str(e)}"


@app.get("/api/consolidator/status/{session_id}")
async def get_processing_status(session_id: str):
    """Check the status of a processing job."""
    if session_id not in jobs:
        raise HTTPException(404, "Session not found")
    job = jobs[session_id]
    return {
        "session_id": session_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
    }


@app.get("/api/consolidator/results/{session_id}")
async def get_consolidator_results(session_id: str):
    """Get the full results: extracted rules + discrepancies."""
    if session_id not in extracted_rules_store:
        raise HTTPException(404, "Results not found. Has processing completed?")

    rules = extracted_rules_store[session_id]
    discs = discrepancies_store.get(session_id, [])
    docs = documents_store.get(session_id, [])

    # Organize rules by category
    by_category = {}
    for r in rules:
        cat = r.category
        sub = r.subcategory
        if cat not in by_category:
            by_category[cat] = {}
        if sub not in by_category[cat]:
            by_category[cat][sub] = []
        by_category[cat][sub].append(asdict(r))

    stats = {
        "total_rules": len(rules),
        "total_discrepancies": len(discs),
        "by_severity": {
            "high": len([d for d in discs if d.severity == "high"]),
            "medium": len([d for d in discs if d.severity == "medium"]),
            "low": len([d for d in discs if d.severity == "low"]),
        },
        "by_automation": {
            "deterministic": len([r for r in rules if r.automatable == "deterministic"]),
            "ai_high": len([r for r in rules if r.automatable == "ai_high"]),
            "ai_moderate": len([r for r in rules if r.automatable == "ai_moderate"]),
            "manual": len([r for r in rules if r.automatable == "manual"]),
        },
        "documents_processed": len(docs),
        "source_files": [d.filename for d in docs],
        "mode": "ai" if HAS_API_KEY else "local",
    }

    return {
        "session_id": session_id,
        "stats": stats,
        "rules_by_category": by_category,
        "discrepancies": discrepancies_to_dict(discs),
    }


# ── Module 2: Quality Checker ──────────────────────────────────────

@app.post("/api/qc/check")
async def run_qc_check(request: QCRequest):
    """Run quality checks on submitted text.
    Deterministic checks always run. AI checks only run if API key is available."""
    if not request.text.strip():
        raise HTTPException(400, "No text provided")

    # Only use AI if key is available AND user requested it
    use_ai = request.use_ai and HAS_API_KEY

    report = run_quality_check(
        document_text=request.text,
        document_name=request.document_name,
        use_ai=use_ai,
    )
    return qc_report_to_dict(report)


@app.get("/api/qc/sample")
async def get_sample_manuscript():
    """Get the sample manuscript for demo purposes."""
    return {"text": SAMPLE_MANUSCRIPT, "name": "Sample: Multi-tissue CRISPR Gene Editing Study"}


@app.post("/api/qc/check-sample")
async def check_sample_manuscript():
    """Run QC on the built-in sample manuscript (for quick demo)."""
    report = run_quality_check(
        document_text=SAMPLE_MANUSCRIPT,
        document_name="Sample: Multi-tissue CRISPR Gene Editing Study",
        use_ai=HAS_API_KEY,
    )
    return qc_report_to_dict(report)


# ── Module 3: Knowledge Agent (RAG) ────────────────────────────────

def _local_knowledge_search(question: str, rules: list) -> dict:
    """Keyword-based search over rules — works without any API."""
    question_lower = question.lower()
    # Extract meaningful keywords (skip stop words)
    stop_words = {"how", "what", "when", "where", "why", "which", "who",
                  "should", "do", "does", "is", "are", "was", "were",
                  "the", "a", "an", "in", "on", "at", "to", "for",
                  "of", "and", "or", "we", "i", "you", "they", "it",
                  "this", "that", "with", "from", "about", "can", "will"}
    keywords = [w for w in re.findall(r'\b[a-z]+\b', question_lower) if w not in stop_words and len(w) > 2]

    # Score each rule by keyword matches
    scored = []
    for r in rules:
        rule_lower = r.rule.lower()
        subcat_lower = r.subcategory.lower()
        source_section = r.source.get("section", "").lower()

        score = 0
        for kw in keywords:
            if kw in rule_lower:
                score += 3
            if kw in subcat_lower:
                score += 2
            if kw in source_section:
                score += 1

        if score > 0:
            scored.append((score, r))

    scored.sort(key=lambda x: -x[0])
    top_rules = scored[:8]

    if not top_rules:
        return {
            "answer": f"I couldn't find specific rules matching your question about \"{question}\". Try rephrasing with keywords like: acronyms, references, spelling, punctuation, abstract, figures, headings, numbers, units, italics, capitalization, hyphenation.",
            "sources": [],
        }

    # Build a readable answer
    answer_parts = [f"Based on the codified style rules, here's what I found about your question:\n"]
    sources = []
    for score, r in top_rules:
        answer_parts.append(f"**[{r.rule_id}]** {r.rule}")
        if r.examples.get("correct"):
            answer_parts.append(f"  Correct: {r.examples['correct'][0]}")
        if r.examples.get("incorrect"):
            answer_parts.append(f"  Incorrect: {r.examples['incorrect'][0]}")
        answer_parts.append(f"  _Source: {r.source.get('document', '?')} — {r.source.get('section', '?')}_\n")
        sources.append({"rule_id": r.rule_id, "rule": r.rule, "source": r.source})

    if not HAS_API_KEY:
        answer_parts.append("\n---\n_Note: Running in local mode (no API key). Answers are based on keyword matching. With an API key, you'd get natural language answers powered by AI._")

    return {
        "answer": "\n".join(answer_parts),
        "sources": sources[:5],
    }


@app.post("/api/knowledge/ask")
async def ask_knowledge_agent(request: KnowledgeQuery):
    """Ask a question about the publisher's style rules.
    Uses AI if available (with caching), otherwise falls back to keyword search."""
    session_id = request.session_id
    rules = extracted_rules_store.get(session_id)

    if not rules:
        return {
            "answer": "No style guide has been processed yet. Please upload and process style guide documents first using the Consolidator, then you can ask questions about the rules.",
            "sources": [],
        }

    # If no API key (and no warm cache), use local keyword search
    if not HAS_API_KEY:
        return _local_knowledge_search(request.question, rules)

    # AI-powered answer via caching layer
    from llm_cache import call_llm, simulate_delay

    rules_context = "\n".join([
        f"- [{r.rule_id}] {r.rule} (Source: {r.source.get('document', 'unknown')})"
        for r in rules
    ])

    if len(rules_context) > 50000:
        rules_context = rules_context[:50000] + "\n[... truncated ...]"

    system_prompt = """You are a knowledgeable style guide assistant for a scientific publisher.
Answer questions based ONLY on the rules provided. If the rules don't cover the question, say so explicitly.
Always cite the rule_id when referencing a specific rule. Be concise and practical."""

    user_prompt = f"STYLE RULES:\n{rules_context}\n\nQUESTION: {request.question}"

    try:
        answer = call_llm(system_prompt, user_prompt, max_tokens=1024)
        simulate_delay()
    except RuntimeError:
        # No API key and cache miss — fall back to local search
        return _local_knowledge_search(request.question, rules)

    referenced = []
    for r in rules:
        if r.rule_id in answer:
            referenced.append({"rule_id": r.rule_id, "rule": r.rule, "source": r.source})

    return {
        "answer": answer,
        "sources": referenced[:5],
    }


# ── Demo endpoints ──────────────────────────────────────────────────

@app.post("/api/demo/load-science-guides")
async def load_science_guides(background_tasks: BackgroundTasks):
    """Load the Science/AAAS style guides from the project directory for instant demo."""
    project_root = Path(__file__).parent.parent.parent
    pdf_files = sorted(project_root.glob("*.pdf"))

    if not pdf_files:
        raise HTTPException(404, "No PDF files found in project directory")

    session_id = "science-demo"
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    file_paths = [str(p) for p in pdf_files]
    mode = "AI (GPT-4.1-mini)" if HAS_API_KEY else "local heuristics"
    jobs[session_id] = {
        "status": "processing",
        "progress": 0,
        "message": f"Loading {len(file_paths)} Science style guide documents... (Mode: {mode})",
        "files": file_paths,
    }

    background_tasks.add_task(_process_session, session_id)
    return {"session_id": session_id, "files_found": len(file_paths), "mode": mode}


@app.post("/api/demo/load-bmj-guides")
async def load_bmj_guides(background_tasks: BackgroundTasks):
    """Load the BMJ style guide from the bmj/ directory for instant demo."""
    project_root = Path(__file__).parent.parent.parent
    bmj_dir = project_root / "bmj"
    pdf_files = sorted(bmj_dir.glob("*.pdf"))

    if not pdf_files:
        raise HTTPException(404, "No PDF files found in bmj/ directory")

    session_id = "bmj-demo"
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    file_paths = [str(p) for p in pdf_files]
    mode = "AI (GPT-4.1-mini)" if HAS_API_KEY else "local heuristics"
    jobs[session_id] = {
        "status": "processing",
        "progress": 0,
        "message": f"Loading {len(file_paths)} BMJ style guide document(s)... (Mode: {mode})",
        "files": file_paths,
    }

    background_tasks.add_task(_process_session, session_id)
    return {"session_id": session_id, "files_found": len(file_paths), "mode": mode}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
