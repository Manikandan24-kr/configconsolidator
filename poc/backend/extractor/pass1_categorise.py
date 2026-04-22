import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_cache import call_llm

VALID_CATEGORIES = [
    "abstract", "acronyms", "capitalization", "hyphenation", "numbers",
    "punctuation", "references", "spelling", "statistical_terms",
    "trademarks", "units", "figures", "general_style",
]

SYSTEM_PROMPT = """You are an expert scholarly publishing editor.
Your task is to identify which editorial rule categories are present in a section of a publisher style guide.
Return ONLY a JSON array of category names. No explanation, no markdown, just the JSON array."""

USER_PROMPT = """Read this section from a publisher style guide.
Identify which of the following categories contain rules in this text.

Categories:
- abstract: rules about abstract content, structure, what can/cannot appear in the abstract
- acronyms: first-use expansion, redefinition, pluralisation, formatting of abbreviations
- capitalization: what to capitalise or lowercase — titles, species, proper nouns, headings
- hyphenation: hyphen vs en-dash, compound modifiers, prefixes, specific term hyphenation
- numbers: spell-out vs numeral rules, ranges, fractions, decimals, leading zeros
- punctuation: commas, apostrophes, colons, semicolons, brackets, ellipsis, dashes
- references: citation format, author truncation, journal abbreviations, DOI, preprints
- spelling: US English preference, preferred spellings, prohibited variant spellings
- statistical_terms: formatting of p-values, CI, SD, SEM, ANOVA, n/N, R² etc.
- trademarks: capitalisation of brand names, generic term usage, no verb/plural/possessive
- units: SI preference, spell-out vs abbreviation, unit spacing, specific unit handling
- figures: captions, panel labels, axis labels, citation rules, figure numbering
- general_style: tense, voice, prohibited terms, jargon, style manual hierarchy

Return ONLY the JSON array of matching category names.
Example: ["hyphenation", "punctuation"]
If no categories match, return: []

Text to analyse:
{text}"""


def categorise_section(text: str) -> list[str]:
    if not text or len(text.strip()) < 50:
        return []

    truncated = text[:6000]
    prompt = USER_PROMPT.format(text=truncated)

    try:
        response = call_llm(SYSTEM_PROMPT, prompt, max_tokens=256)
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(
                l for l in lines if not l.startswith("```")
            ).strip()
        categories = json.loads(response)
        if isinstance(categories, list):
            return [c for c in categories if c in VALID_CATEGORIES]
        return []
    except Exception:
        return _heuristic_categorise(text)


def _heuristic_categorise(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    keywords = {
        "abstract": ["abstract", "summary"],
        "acronyms": ["acronym", "abbreviation", "first use", "spell out"],
        "capitalization": ["capitaliz", "capitalise", "uppercase", "lowercase", "cap "],
        "hyphenation": ["hyphen", "en dash", "en-dash", "compound"],
        "numbers": ["numeral", "number", "digit", "spell out", "fraction", "decimal"],
        "punctuation": ["comma", "apostrophe", "colon", "semicolon", "bracket", "ellipsis", "dash"],
        "references": ["reference", "citation", "bibliography", "cite", "doi"],
        "spelling": ["spelling", "british", "american", "us english", "preferred form"],
        "statistical_terms": ["p value", "p-value", "confidence interval", "standard deviation", "anova", "statistical"],
        "trademarks": ["trademark", "brand name", "trade name", "proprietary"],
        "units": ["unit", "si ", "metric", "abbreviat"],
        "figures": ["figure", "caption", "panel", "axis", "legend", "table"],
        "general_style": ["tense", "active voice", "passive voice", "novel", "jargon", "style manual"],
    }
    for category, words in keywords.items():
        if any(w in text_lower for w in words):
            found.append(category)
    return found
