"""
AI-powered rule extraction engine.
Uses OpenAI GPT-4.1-mini (via caching layer) to extract structured editorial
and typesetting rules from style guide text.
"""
import json
from dataclasses import dataclass, field, asdict
from llm_cache import call_llm, simulate_delay

EXTRACTION_SYSTEM_PROMPT = """You are an expert publishing style guide analyst working for Kriyadocs, a scholarly publishing platform. Your job is to extract precise, actionable rules from publisher style guide documents.

For each rule you extract, provide:
1. A unique rule_id (category.subcategory.number format, e.g., "spelling.dialect.1")
2. The category (editorial, typesetting, references, communication)
3. The subcategory (e.g., spelling, punctuation, tense, headings, figures, etc.)
4. A clear, concise rule statement
5. Examples (correct and incorrect) when available
6. Exceptions to the rule when stated
7. The source (which document section this came from)
8. How automatable this rule is: "deterministic" (regex/dictionary), "ai_high" (AI can reliably check), "ai_moderate" (AI can sometimes check), "manual" (needs human)

Output valid JSON only. No markdown, no commentary outside the JSON."""

EXTRACTION_USER_PROMPT = """Analyze this style guide content and extract ALL rules into structured JSON.

DOCUMENT: {filename}
SECTION: {section_title}

CONTENT:
{content}

Return a JSON object with this exact structure:
{{
  "rules": [
    {{
      "rule_id": "category.subcategory.number",
      "category": "editorial|typesetting|references|communication",
      "subcategory": "string",
      "rule": "Clear statement of the rule",
      "examples": {{
        "correct": ["example1", "example2"],
        "incorrect": ["example1", "example2"]
      }},
      "exceptions": ["exception1"],
      "source": {{
        "document": "filename",
        "section": "section title"
      }},
      "automatable": "deterministic|ai_high|ai_moderate|manual",
      "automation_notes": "Brief note on how to automate or why it can't be"
    }}
  ]
}}"""


CONFLICT_SYSTEM_PROMPT = """You are an expert style guide analyst. Your job is to analyze a set of extracted rules and find:

1. CONFLICTS: Rules that contradict each other (e.g., one says use serial comma, another implies don't)
2. AMBIGUITIES: Rules that are vague or could be interpreted multiple ways
3. GAPS: Important areas commonly covered by style guides that are missing here
4. OVERLAPS: Rules from different documents that say the same thing (redundancy)

Be specific. Quote the actual rules by their rule_id. Only flag genuine issues, not trivial ones."""

CONFLICT_USER_PROMPT = """Analyze these extracted rules for conflicts, ambiguities, gaps, and overlaps.

RULES:
{rules_json}

Return a JSON object:
{{
  "discrepancies": [
    {{
      "type": "conflict|ambiguity|gap|overlap",
      "severity": "high|medium|low",
      "title": "Short description",
      "description": "Detailed explanation",
      "affected_rules": ["rule_id_1", "rule_id_2"],
      "recommendation": "What the publisher should clarify or decide"
    }}
  ]
}}"""


@dataclass
class ExtractedRule:
    rule_id: str
    category: str
    subcategory: str
    rule: str
    examples: dict = field(default_factory=lambda: {"correct": [], "incorrect": []})
    exceptions: list = field(default_factory=list)
    source: dict = field(default_factory=dict)
    automatable: str = "manual"
    automation_notes: str = ""


@dataclass
class Discrepancy:
    type: str
    severity: str
    title: str
    description: str
    affected_rules: list = field(default_factory=list)
    recommendation: str = ""


def _call_llm(system: str, user: str, max_tokens: int = 4096) -> str:
    """Call LLM via the caching abstraction layer."""
    return call_llm(system, user, max_tokens)


def _parse_json_response(text: str) -> dict:
    """Robustly parse JSON from LLM response, handling markdown wrappers."""
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (``` markers)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


def extract_rules_from_section(filename: str, section_title: str, content: str) -> list[ExtractedRule]:
    """Use LLM to extract rules from a single section of text."""
    if len(content.strip()) < 50:
        return []

    # Truncate very long sections to stay within token limits
    if len(content) > 8000:
        content = content[:8000] + "\n[... truncated for processing ...]"

    prompt = EXTRACTION_USER_PROMPT.format(
        filename=filename,
        section_title=section_title,
        content=content,
    )

    try:
        response = _call_llm(EXTRACTION_SYSTEM_PROMPT, prompt, max_tokens=4096)
        simulate_delay()
        data = _parse_json_response(response)
        rules = []
        for r in data.get("rules", []):
            rules.append(ExtractedRule(
                rule_id=r.get("rule_id", "unknown"),
                category=r.get("category", "editorial"),
                subcategory=r.get("subcategory", "general"),
                rule=r.get("rule", ""),
                examples=r.get("examples", {"correct": [], "incorrect": []}),
                exceptions=r.get("exceptions", []),
                source=r.get("source", {"document": filename, "section": section_title}),
                automatable=r.get("automatable", "manual"),
                automation_notes=r.get("automation_notes", ""),
            ))
        return rules
    except Exception as e:
        print(f"Warning: Rule extraction failed for {filename}/{section_title}: {e}")
        return []


def detect_discrepancies(rules: list[ExtractedRule]) -> list[Discrepancy]:
    """Use LLM to analyze all extracted rules for conflicts and gaps."""
    if not rules:
        return []

    # Send a summary of rules (not full details, to manage token usage)
    rules_summary = []
    for r in rules:
        rules_summary.append({
            "rule_id": r.rule_id,
            "category": r.category,
            "subcategory": r.subcategory,
            "rule": r.rule,
            "source": r.source,
        })

    # Chunk if too many rules
    chunk_size = 80
    all_discrepancies = []

    for i in range(0, len(rules_summary), chunk_size):
        chunk = rules_summary[i:i + chunk_size]
        prompt = CONFLICT_USER_PROMPT.format(rules_json=json.dumps(chunk, indent=2))

        try:
            response = _call_llm(CONFLICT_SYSTEM_PROMPT, prompt, max_tokens=4096)
            simulate_delay()
            data = _parse_json_response(response)
            for d in data.get("discrepancies", []):
                all_discrepancies.append(Discrepancy(
                    type=d.get("type", "ambiguity"),
                    severity=d.get("severity", "medium"),
                    title=d.get("title", ""),
                    description=d.get("description", ""),
                    affected_rules=d.get("affected_rules", []),
                    recommendation=d.get("recommendation", ""),
                ))
        except Exception as e:
            print(f"Warning: Discrepancy detection failed for chunk {i}: {e}")

    return all_discrepancies


def rules_to_dict(rules: list[ExtractedRule]) -> list[dict]:
    """Convert rules to serializable dicts."""
    return [asdict(r) for r in rules]


def discrepancies_to_dict(discs: list[Discrepancy]) -> list[dict]:
    """Convert discrepancies to serializable dicts."""
    return [asdict(d) for d in discs]
