import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_cache import call_llm

SYSTEM_PROMPT = """You are an expert scholarly publishing copyeditor working for Kriyadocs.
Extract pre-editing rules from publisher style guide text.
Return ONLY valid JSON. No markdown, no explanation."""

CATEGORY_FOCUS = {
    "abstract": "rules about abstract content — what can and cannot appear, structure, tense, word limits, how to handle acronyms/units/citations within the abstract",
    "acronyms": "rules about abbreviations and acronyms — first-use expansion, when to define, redefinition in abstract vs main text, pluralisation, capitalisation of acronyms, accepted-as-is acronyms",
    "capitalization": "rules about what to capitalise or lowercase — article titles, subheadings, genus/species names, proper nouns, government titles, geographic terms, scientific terms",
    "hyphenation": "rules about hyphens and dashes — compound modifiers, prefixes (non-, pre-, anti-), en-dash usage, specific terms to hyphenate or not hyphenate",
    "numbers": "rules about numbers — when to spell out vs use numerals, ranges, fractions, decimals, leading zeros, large numbers, ordinals, percentages",
    "punctuation": "rules about punctuation marks — commas (serial/Oxford, appositive), apostrophes (possessives, plurals), colons, semicolons, parentheses, brackets, ellipsis, em/en dashes",
    "references": "rules about citations and reference lists — citation style, author name formatting, author truncation (et al.), journal abbreviations, DOI formatting, book citations, preprints, online sources",
    "spelling": "rules about preferred spellings — US vs British English, specific preferred forms (e.g. 'waveform' not 'wave form'), prohibited variant spellings",
    "statistical_terms": "rules about statistical notation — formatting of p-values, confidence intervals, SD, SEM, ANOVA, df, n/N, R², OR, formatting of test names",
    "trademarks": "rules about trademarked and brand names — capitalisation, using generic term alongside trademark, not using trademarks as verbs or plurals or possessives",
    "units": "rules about units of measurement — SI/metric preference, when to spell out vs abbreviate, spacing between number and unit, specific unit handling instructions",
    "figures": "rules about figures and tables — caption structure, panel label formatting, axis label requirements, how to cite figures in text, figure numbering conventions",
    "general_style": "rules about overall writing style — tense (past for results, present for conclusions), voice (active vs passive), prohibited terms (novel, unique, first, data not shown), jargon avoidance, style manual hierarchy",
}

USER_PROMPT = """Extract ONLY {category} rules from this publisher style guide text.

Focus area: {focus}

Rules for a good extraction:
1. One rule = one actionable instruction a copyeditor applies to a manuscript
2. Write as a clear imperative sentence (e.g. "Do not cite references in the abstract.")
3. Include exceptions within the same rule if they are stated (e.g. "Spell out units in the abstract, except M for molar concentration.")
4. Do NOT extract background explanations or rationale — only the instruction
5. Do NOT invent or infer rules — only extract what is explicitly stated in the text
6. Do NOT duplicate rules that express the same instruction in different words

Return ONLY this JSON structure:
{{
  "rules": [
    {{
      "rule": "clear imperative instruction as one sentence",
      "source_section": "the heading or section this came from",
      "remarks": "any important nuance not captured in the rule itself (optional, omit if none)"
    }}
  ]
}}

Style guide text:
{text}"""


def extract_rules_for_category(
    text: str,
    category: str,
    source_section: str = "",
) -> list[dict]:
    if not text or len(text.strip()) < 30:
        return []
    if category not in CATEGORY_FOCUS:
        return []

    truncated = text[:8000]
    focus = CATEGORY_FOCUS[category]
    prompt = USER_PROMPT.format(category=category, focus=focus, text=truncated)

    try:
        response = call_llm(SYSTEM_PROMPT, prompt, max_tokens=4096)
        return _parse_rules(response, source_section)
    except Exception:
        return []


def _parse_rules(response: str, fallback_section: str) -> list[dict]:
    response = response.strip()
    if response.startswith("```"):
        lines = response.split("\n")
        response = "\n".join(
            l for l in lines if not l.startswith("```")
        ).strip()

    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                data = json.loads(response[start:end])
            except Exception:
                return []
        else:
            return []

    rules = []
    for item in data.get("rules", []):
        rule_text = str(item.get("rule", "")).strip()
        if len(rule_text) < 10:
            continue
        rules.append({
            "rule": rule_text,
            "source_section": item.get("source_section") or fallback_section,
            "remarks": item.get("remarks") or None,
        })
    return rules
