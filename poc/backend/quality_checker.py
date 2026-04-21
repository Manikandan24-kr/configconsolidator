"""
Quality Checker engine — validates documents against extracted rules with confidence scoring.
Deterministic checks run instantly; AI checks use OpenAI GPT-4.1-mini (via caching layer) for nuanced analysis.
"""
import re
import json
from dataclasses import dataclass, field, asdict
from llm_cache import call_llm, simulate_delay


@dataclass
class QCIssue:
    rule_id: str
    rule_text: str
    severity: str  # "error", "warning", "info"
    confidence: str  # "definitive", "high", "moderate", "low"
    confidence_pct: int  # 0-100
    location: str  # line/paragraph reference
    found_text: str  # the problematic text
    suggestion: str  # what to change
    category: str  # editorial, typesetting, references


@dataclass
class QCReport:
    document_name: str
    total_rules_checked: int
    issues: list[QCIssue] = field(default_factory=list)
    unchecked_rules: list[dict] = field(default_factory=list)  # rules that need human review


# ── Deterministic Checks ──────────────────────────────────────────────

BRITISH_TO_US = {
    "colour": "color", "colours": "colors", "favour": "favor", "favours": "favors",
    "behaviour": "behavior", "behaviours": "behaviors", "honour": "honor",
    "labour": "labor", "neighbour": "neighbor", "tumour": "tumor",
    "tumours": "tumors", "analyse": "analyze", "analysed": "analyzed",
    "catalyse": "catalyze", "characterise": "characterize",
    "characterised": "characterized", "colonise": "colonize",
    "crystallise": "crystallize", "fertilise": "fertilize",
    "finalise": "finalize", "hospitalise": "hospitalize",
    "immunise": "immunize", "maximise": "maximize", "minimise": "minimize",
    "normalise": "normalize", "optimise": "optimize", "organise": "organize",
    "organised": "organized", "organisation": "organization",
    "oxidise": "oxidize", "paralyse": "paralyze", "pasteurise": "pasteurize",
    "polarise": "polarize", "polymerise": "polymerize",
    "randomise": "randomize", "randomised": "randomized",
    "realise": "realize", "recognised": "recognized", "recognise": "recognize",
    "specialise": "specialize", "standardise": "standardize",
    "summarise": "summarize", "sympathise": "sympathize",
    "synthesise": "synthesize", "utilise": "utilize",
    "visualise": "visualize", "centre": "center", "centres": "centers",
    "fibre": "fiber", "fibres": "fibers", "litre": "liter", "litres": "liters",
    "metre": "meter", "metres": "meters", "theatre": "theater",
    "defence": "defense", "licence": "license", "offence": "offense",
    "practise": "practice", "grey": "gray", "ageing": "aging",
    "foetus": "fetus", "foetal": "fetal", "haemoglobin": "hemoglobin",
    "haemorrhage": "hemorrhage", "leukaemia": "leukemia",
    "oedema": "edema", "oesophagus": "esophagus", "oestrogen": "estrogen",
    "paediatric": "pediatric", "anaemia": "anemia", "anaesthesia": "anesthesia",
    "diarrhoea": "diarrhea", "gynaecology": "gynecology",
    "haematology": "hematology", "modelling": "modeling",
    "labelling": "labeling", "travelling": "traveling",
    "signalling": "signaling", "cancelling": "canceling",
    "fulfil": "fulfill", "enrol": "enroll", "skilful": "skillful",
    "catalogue": "catalog", "analogue": "analog", "dialogue": "dialog",
    "programme": "program", "judgement": "judgment",
}

PROHIBITED_TERMS_SCIENCE = [
    {"term": "novel", "context": r"\bnovel\b", "note": "Avoid 'novel' to describe findings; use 'previously unidentified' or 'unexpected'"},
    {"term": "unique", "context": r"\bunique\b", "note": "Avoid 'unique' unless truly one of a kind"},
    {"term": "for the first time", "context": r"for the first time", "note": "Remove claims of priority; Science reports new developments by definition"},
    {"term": "new", "context": r"\bnew\b(?!\s+York|\s+Jersey|\s+Zealand|\s+England|\s+Hampshire|\s+Mexico)", "note": "Consider removing 'new' when describing findings — may be redundant in Science context"},
    {"term": "our laboratory has pioneered", "context": r"(?:our|we)\s+(?:laboratory|lab|group)\s+(?:has|have)\s+pioneered", "note": "Remove claims of being first/pioneering"},
    {"term": "data not shown", "context": r"data\s+not\s+shown", "note": "'Data not shown' should be deleted or moved to supplementary materials"},
    {"term": "in the literature", "context": r"in the literature", "note": "Vague reference — add specific citations or remove"},
    {"term": "it is well known", "context": r"it is (?:well[- ])?known", "note": "Remove unsupported general claims; add citation or delete"},
    {"term": "note that", "context": r"\bnote that\b", "note": "Delete 'note that' and similar instructions to the reader"},
    {"term": "there are/is", "context": r"\bthere (?:are|is|were|was)\b", "note": "Consider rewriting to avoid expletive construction ('there are')"},
]


def _check_spelling_dialect(text: str, lines: list[str]) -> list[QCIssue]:
    """Check for British spellings that should be US English."""
    issues = []
    for i, line in enumerate(lines, 1):
        words = re.findall(r'\b[a-z]+\b', line.lower())
        for word in words:
            if word in BRITISH_TO_US:
                issues.append(QCIssue(
                    rule_id="spelling.dialect.us_english",
                    rule_text="Use U.S. English spellings only (except in author affiliations, organization names, journal titles, and book titles)",
                    severity="error",
                    confidence="definitive",
                    confidence_pct=98,
                    location=f"Line {i}",
                    found_text=word,
                    suggestion=f'Change "{word}" to "{BRITISH_TO_US[word]}"',
                    category="editorial",
                ))
    return issues


def _check_prohibited_terms(text: str, lines: list[str]) -> list[QCIssue]:
    """Check for terms Science style prohibits or discourages."""
    issues = []
    for i, line in enumerate(lines, 1):
        for term_info in PROHIBITED_TERMS_SCIENCE:
            matches = list(re.finditer(term_info["context"], line, re.IGNORECASE))
            for m in matches:
                # "new" is only moderate confidence since context matters a lot
                conf = "high" if term_info["term"] != "new" else "moderate"
                pct = 85 if conf == "high" else 60
                if term_info["term"] in ("there are/is", "note that"):
                    conf = "moderate"
                    pct = 65
                issues.append(QCIssue(
                    rule_id=f"editorial.prohibited.{term_info['term'].replace(' ', '_')}",
                    rule_text=term_info["note"],
                    severity="warning",
                    confidence=conf,
                    confidence_pct=pct,
                    location=f"Line {i}",
                    found_text=m.group(),
                    suggestion=term_info["note"],
                    category="editorial",
                ))
    return issues


def _check_abstract_rules(text: str) -> list[QCIssue]:
    """Check abstract-specific rules if an abstract section is detected."""
    issues = []
    abstract_match = re.search(r'(?:^|\n)(?:Abstract|ABSTRACT)[:\s]*\n?(.*?)(?:\n\n|\n(?:[A-Z]{2,})|\Z)', text, re.DOTALL | re.IGNORECASE)
    if abstract_match:
        abstract_text = abstract_match.group(1).strip()
        word_count = len(abstract_text.split())
        if word_count > 125:
            issues.append(QCIssue(
                rule_id="abstract.length.max_125",
                rule_text="Abstract length should be 125 words or less",
                severity="error",
                confidence="definitive",
                confidence_pct=99,
                location="Abstract",
                found_text=f"Abstract is {word_count} words",
                suggestion=f"Reduce abstract by {word_count - 125} words (currently {word_count}, max 125)",
                category="editorial",
            ))

        # Check for references in abstract
        ref_pattern = re.findall(r'\(\d+\)|\[\d+\]|et al\.\s*\(', abstract_text)
        if ref_pattern:
            issues.append(QCIssue(
                rule_id="abstract.no_references",
                rule_text="Do not cite references in the abstract",
                severity="error",
                confidence="high",
                confidence_pct=90,
                location="Abstract",
                found_text=str(ref_pattern[:3]),
                suggestion="Remove reference citations from the abstract",
                category="editorial",
            ))

        # Check for figure/table citations in abstract
        fig_pattern = re.findall(r'(?:Fig(?:ure)?|Table)\s*\.?\s*\d+', abstract_text, re.IGNORECASE)
        if fig_pattern:
            issues.append(QCIssue(
                rule_id="abstract.no_figures_tables",
                rule_text="Do not cite figures or tables in the abstract",
                severity="error",
                confidence="definitive",
                confidence_pct=97,
                location="Abstract",
                found_text=str(fig_pattern[:3]),
                suggestion="Remove figure/table citations from the abstract",
                category="editorial",
            ))
    return issues


def _check_acronym_first_use(text: str, lines: list[str]) -> list[QCIssue]:
    """Check that acronyms are spelled out at first use."""
    issues = []
    # Find all uppercase acronyms (2+ letters)
    acronym_pattern = re.compile(r'\b([A-Z]{2,}[0-9]*)\b')
    # Common acronyms that don't need expansion (units, common)
    skip = {"US", "USA", "UK", "DNA", "RNA", "HIV", "AIDS", "NASA", "PhD",
            "OK", "AM", "PM", "AD", "BC", "CEO", "CFO", "COO", "CTO",
            "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII",
            "SI", "AND", "OR", "NOT", "THE", "FOR", "BUT", "NOR", "YET",
            "WITH", "FROM", "INTO", "UPON", "ABOUT", "AFTER", "ALSO",
            "BOTH", "EACH", "EVEN", "HAS", "HAVE", "HER", "HIS", "ITS",
            "MAY", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY",
            "DID", "GET", "HIM", "LET", "SAY", "SHE", "TOO", "USE",
            "SM", "PDF", "FIG", "EQ", "REF", "REFS", "ED", "EDS",
            "VOL", "PP", "VS", "AAAS"}

    seen_acronyms = {}
    for i, line in enumerate(lines, 1):
        for m in acronym_pattern.finditer(line):
            acr = m.group(1)
            if acr in skip or len(acr) < 2:
                continue
            if acr not in seen_acronyms:
                seen_acronyms[acr] = i
                # Check if it's expanded nearby (within same line or previous line)
                search_window = line
                if i > 1:
                    search_window = lines[i - 2] + " " + line
                # Look for parenthetical definition: "full name (ACRONYM)" or "(ACRONYM)"
                expanded_pattern = rf'\w[\w\s]{{2,}}\({re.escape(acr)}\)'
                if not re.search(expanded_pattern, search_window):
                    issues.append(QCIssue(
                        rule_id="acronym.first_use_expansion",
                        rule_text="Spell out all acronyms and abbreviations the first time they are mentioned in the text",
                        severity="warning",
                        confidence="high",
                        confidence_pct=82,
                        location=f"Line {i}",
                        found_text=acr,
                        suggestion=f'Acronym "{acr}" appears to not be expanded at first use — spell it out followed by ({acr})',
                        category="editorial",
                    ))
    return issues


def _check_title_length(text: str, lines: list[str]) -> list[QCIssue]:
    """Check that the title doesn't exceed 96 characters."""
    issues = []
    # Heuristic: first non-empty line might be the title
    for i, line in enumerate(lines[:5], 1):
        stripped = line.strip()
        if stripped and len(stripped) > 96 and i <= 2:
            issues.append(QCIssue(
                rule_id="title.max_96_chars",
                rule_text="Titles cannot exceed 96 characters and spaces total; four-line titles are not allowed",
                severity="error",
                confidence="moderate",
                confidence_pct=70,
                location=f"Line {i} (possible title)",
                found_text=f'"{stripped[:60]}..." ({len(stripped)} chars)',
                suggestion=f"Title appears to be {len(stripped)} characters — max is 96",
                category="editorial",
            ))
    return issues


def _check_contractions(text: str, lines: list[str]) -> list[QCIssue]:
    """Check for contractions which Science style avoids."""
    issues = []
    contraction_pattern = re.compile(
        r"\b(you're|he's|she's|it's|we're|they're|I'm|isn't|aren't|wasn't|weren't|"
        r"don't|doesn't|didn't|won't|wouldn't|couldn't|shouldn't|can't|hasn't|haven't)\b",
        re.IGNORECASE
    )
    expansions = {
        "you're": "you are", "he's": "he is", "she's": "she is",
        "it's": "it is", "we're": "we are", "they're": "they are",
        "i'm": "I am", "isn't": "is not", "aren't": "are not",
        "wasn't": "was not", "weren't": "were not", "don't": "do not",
        "doesn't": "does not", "didn't": "did not", "won't": "will not",
        "wouldn't": "would not", "couldn't": "could not",
        "shouldn't": "should not", "can't": "cannot",
        "hasn't": "has not", "haven't": "have not",
    }
    for i, line in enumerate(lines, 1):
        for m in contraction_pattern.finditer(line):
            word = m.group(1).lower()
            issues.append(QCIssue(
                rule_id="editorial.contractions.avoid",
                rule_text="At Science, we rarely use contractions. Use the expanded form.",
                severity="warning",
                confidence="definitive",
                confidence_pct=95,
                location=f"Line {i}",
                found_text=m.group(1),
                suggestion=f'Change "{m.group(1)}" to "{expansions.get(word, word)}"',
                category="editorial",
            ))
    return issues


def _check_reference_format(text: str, lines: list[str]) -> list[QCIssue]:
    """Basic reference format checks for Science style."""
    issues = []
    in_refs = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r'^(?:References|REFERENCES|References and Notes)', stripped):
            in_refs = True
            continue
        if not in_refs:
            continue
        if not stripped:
            continue
        # Check for numbered reference
        ref_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if ref_match:
            ref_text = ref_match.group(2)
            # Check: author names should have initials first
            # Pattern: "J. C. Smith" (correct) vs "Smith J.C." (incorrect)
            if re.match(r'^[A-Z][a-z]+\s+[A-Z]\.', ref_text):
                issues.append(QCIssue(
                    rule_id="references.author_format.initials_first",
                    rule_text="List initials first (separated by a space) for author names in citations",
                    severity="error",
                    confidence="high",
                    confidence_pct=88,
                    location=f"Line {i} (Ref {ref_match.group(1)})",
                    found_text=ref_text[:60],
                    suggestion="Author names should list initials first, e.g., 'J. C. Smith' not 'Smith J. C.'",
                    category="references",
                ))
            # Check: "and" between authors (should not be used in Science style)
            if " and " in ref_text.split(",")[0] if "," in ref_text else " and " in ref_text[:80]:
                # Only flag if it appears to be between author names
                if re.search(r'[A-Z]\.\s+\w+\s+and\s+[A-Z]\.', ref_text[:80]):
                    issues.append(QCIssue(
                        rule_id="references.author_format.no_and",
                        rule_text="Do not use 'and' between author names in references",
                        severity="warning",
                        confidence="high",
                        confidence_pct=85,
                        location=f"Line {i} (Ref {ref_match.group(1)})",
                        found_text=ref_text[:60],
                        suggestion="Remove 'and' between author names; separate with commas only",
                        category="references",
                    ))
    return issues


# ── AI-Powered Checks ──────────────────────────────────────────────

AI_QC_SYSTEM_PROMPT = """You are a meticulous copy editor checking a scientific manuscript against the Science/AAAS style guide. Analyze the text for:

1. TENSE ISSUES: Past tense for experimental results, present tense for conclusions/established facts
2. VOICE ISSUES: Active voice preferred in certain contexts
3. WORDINESS: Unnecessary words, redundant phrases
4. CLARITY: Dangling modifiers, freight-train modifiers, unclear antecedents
5. STYLE: Avoid overediting language, but flag clear style violations

For each issue found, provide:
- The problematic text (exact quote)
- Which line it's on (approximate)
- What rule it violates
- Your confidence (0-100)
- A suggested fix

Only flag genuine issues. Do not over-flag. Quality over quantity.
Return valid JSON only."""

AI_QC_USER_PROMPT = """Check this manuscript text against Science style rules. Focus on the nuanced rules that require language understanding (tense, voice, wordiness, clarity).

TEXT:
{text}

Return JSON:
{{
  "issues": [
    {{
      "rule_id": "editorial.tense|voice|wordiness|clarity.description",
      "rule_text": "The rule being violated",
      "severity": "error|warning|info",
      "confidence_pct": 50-95,
      "location": "Line N or paragraph description",
      "found_text": "exact problematic text",
      "suggestion": "what to change and why"
    }}
  ]
}}"""


def _run_ai_checks(text: str) -> list[QCIssue]:
    """Use LLM for nuanced style checks that require language understanding."""
    check_text = text[:6000] if len(text) > 6000 else text

    try:
        response_text = call_llm(
            system=AI_QC_SYSTEM_PROMPT,
            user=AI_QC_USER_PROMPT.format(text=check_text),
            max_tokens=4096,
        )
        simulate_delay()

        response_text = response_text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = "\n".join(lines)

        data = json.loads(response_text)
        issues = []
        for item in data.get("issues", []):
            pct = item.get("confidence_pct", 60)
            if pct >= 80:
                conf = "high"
            elif pct >= 50:
                conf = "moderate"
            else:
                conf = "low"
            issues.append(QCIssue(
                rule_id=item.get("rule_id", "ai.check"),
                rule_text=item.get("rule_text", ""),
                severity=item.get("severity", "warning"),
                confidence=conf,
                confidence_pct=pct,
                location=item.get("location", ""),
                found_text=item.get("found_text", ""),
                suggestion=item.get("suggestion", ""),
                category="editorial",
            ))
        return issues
    except Exception as e:
        print(f"AI QC check failed: {e}")
        return []


# ── Manual/Unchecked Rules ─────────────────────────────────────────

UNCHECKED_RULES = [
    {"rule_id": "abstract.structure", "rule": "Abstract should follow: broad intro → specific background → results → conclusions", "reason": "Requires deep semantic understanding of scientific content"},
    {"rule_id": "figures.legend_quality", "rule": "Figure legends should be brief descriptions of the content", "reason": "Requires visual analysis of figures"},
    {"rule_id": "affiliations.accuracy", "rule": "Affiliations should correspond to where work was done", "reason": "Requires external verification"},
    {"rule_id": "editorial.metaphors", "rule": "Editors should be mindful of metaphors and figures of speech", "reason": "Highly subjective, requires cultural context"},
    {"rule_id": "editorial.jargon", "rule": "Avoid laboratory jargon specific to certain disciplines", "reason": "Requires deep domain expertise to identify"},
    {"rule_id": "editorial.overediting", "rule": "Avoid overediting; retain the author's language as much as possible", "reason": "Requires editorial judgment about author intent"},
    {"rule_id": "references.accuracy", "rule": "All Science references should be checked for accuracy", "reason": "Requires cross-referencing with external databases"},
    {"rule_id": "dedication.deceased", "rule": "Dedications allowed only when subject is deceased", "reason": "Requires external fact verification"},
]


# ── Main QC Runner ──────────────────────────────────────────────────

def run_quality_check(document_text: str, document_name: str = "document", use_ai: bool = True) -> QCReport:
    """Run all quality checks on a document and produce a report."""
    lines = document_text.split("\n")

    all_issues = []

    # Deterministic checks (instant, high confidence)
    all_issues.extend(_check_spelling_dialect(document_text, lines))
    all_issues.extend(_check_prohibited_terms(document_text, lines))
    all_issues.extend(_check_abstract_rules(document_text))
    all_issues.extend(_check_acronym_first_use(document_text, lines))
    all_issues.extend(_check_title_length(document_text, lines))
    all_issues.extend(_check_contractions(document_text, lines))
    all_issues.extend(_check_reference_format(document_text, lines))

    deterministic_count = len(all_issues)

    # AI-powered checks (nuanced, variable confidence)
    if use_ai:
        ai_issues = _run_ai_checks(document_text)
        all_issues.extend(ai_issues)

    # Sort by confidence (highest first), then by severity
    severity_order = {"error": 0, "warning": 1, "info": 2}
    all_issues.sort(key=lambda x: (severity_order.get(x.severity, 2), -x.confidence_pct))

    total_checked = deterministic_count + (7 if use_ai else 0) + len(UNCHECKED_RULES)

    return QCReport(
        document_name=document_name,
        total_rules_checked=total_checked,
        issues=all_issues,
        unchecked_rules=UNCHECKED_RULES,
    )


def qc_report_to_dict(report: QCReport) -> dict:
    return {
        "document_name": report.document_name,
        "total_rules_checked": report.total_rules_checked,
        "summary": {
            "definitive_issues": len([i for i in report.issues if i.confidence == "definitive"]),
            "high_confidence_issues": len([i for i in report.issues if i.confidence == "high"]),
            "moderate_confidence_issues": len([i for i in report.issues if i.confidence == "moderate"]),
            "low_confidence_issues": len([i for i in report.issues if i.confidence == "low"]),
            "unchecked_rules": len(report.unchecked_rules),
        },
        "issues": [asdict(i) for i in report.issues],
        "unchecked_rules": report.unchecked_rules,
    }
