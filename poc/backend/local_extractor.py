"""
Local (offline) rule extraction engine — works WITHOUT any API key.
Uses heuristic pattern matching to extract rules from style guide text.
Less sophisticated than the AI extractor, but produces real, usable results.
"""
import re
from dataclasses import dataclass, field, asdict


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


# ── Category detection from filename / title ──────────────────────

CATEGORY_MAP = {
    "abstract": ("editorial", "abstract"),
    "acronym": ("editorial", "acronyms"),
    "affiliation": ("editorial", "affiliations"),
    "capitalization": ("editorial", "capitalization"),
    "figure": ("typesetting", "figures_tables"),
    "table": ("typesetting", "figures_tables"),
    "equation": ("typesetting", "equations"),
    "general": ("editorial", "general_style"),
    "hyphen": ("editorial", "hyphenation"),
    "italic": ("typesetting", "italics"),
    "number": ("editorial", "numbers"),
    "organization": ("editorial", "organizations"),
    "punctuation": ("editorial", "punctuation"),
    "reference": ("references", "references"),
    "spelling": ("editorial", "spelling"),
    "statistic": ("editorial", "statistics"),
    "trademark": ("editorial", "trademarks"),
    "unit": ("editorial", "units"),
    "cmos": ("editorial", "hyphenation"),
}


def _detect_category(filename: str) -> tuple:
    """Detect rule category from filename."""
    name_lower = filename.lower()
    for keyword, (cat, sub) in CATEGORY_MAP.items():
        if keyword in name_lower:
            return cat, sub
    return "editorial", "general"


# ── Rule extraction patterns ──────────────────────────────────────

def _is_rule_line(line: str) -> bool:
    """Heuristic: is this line likely stating a rule?"""
    line = line.strip()
    if not line or len(line) < 20:
        return False
    # Lines starting with dash, bullet, number, or imperative verbs
    if re.match(r'^[-–—•]\s*', line):
        return True
    if re.match(r'^\d+[\.\)]\s+', line):
        return True
    # Imperative mood indicators
    imperative_starts = [
        "use ", "do not ", "don't ", "avoid ", "always ", "never ",
        "spell ", "write ", "abbreviate ", "capitalize ", "italicize ",
        "delete ", "remove ", "change ", "include ", "list ", "place ",
        "retain ", "set ", "check ", "make sure", "be careful",
        "editors should", "copyeditors should", "proofreaders should",
        "try to ", "prefer ", "we use ", "we do not", "at science",
        "for all ", "for a ", "all ", "the first ", "when ",
    ]
    lower = line.lower()
    for start in imperative_starts:
        if lower.startswith(start):
            return True
    # Contains "should" or "must" (prescriptive language)
    if " should " in lower or " must " in lower:
        return True
    return False


def _extract_examples(lines: list, start_idx: int) -> dict:
    """Look for correct/incorrect examples near a rule."""
    examples = {"correct": [], "incorrect": []}
    # Search the next few lines for example patterns
    for j in range(start_idx + 1, min(start_idx + 8, len(lines))):
        line = lines[j].strip()
        lower = line.lower()
        if lower.startswith(("ex:", "example:", "e.g.,")):
            examples["correct"].append(line)
        elif lower.startswith(("correct:", "to:")):
            examples["correct"].append(line.split(":", 1)[1].strip())
        elif lower.startswith(("incorrect:", "change:", "*")):
            examples["incorrect"].append(line.split(":", 1)[1].strip() if ":" in line else line)
    return examples


def _classify_automation(rule_text: str) -> tuple:
    """Classify how automatable a rule is."""
    lower = rule_text.lower()

    # Deterministic patterns
    deterministic_keywords = [
        "spell out", "abbreviat", "capitalize", "lowercase", "uppercase",
        "italic", "bold", "roman", "do not use", "should not be used",
        "use u.s. english", "american english", "british",
        "maximum", "cannot exceed", "no longer than", "words or less",
        "use periods", "no comma before", "serial comma",
        "superscript", "subscript", "parenthes",
    ]
    for kw in deterministic_keywords:
        if kw in lower:
            return "deterministic", f"Can be checked via pattern matching / dictionary ({kw})"

    # AI-checkable patterns
    ai_high_keywords = [
        "avoid", "delete unnecessary", "remove",
        "should be in the past", "past tense", "present tense",
        "active voice", "passive voice", "reword", "recast",
    ]
    for kw in ai_high_keywords:
        if kw in lower:
            return "ai_high", f"AI can reliably detect ({kw})"

    ai_moderate_keywords = [
        "wordiness", "redundan", "clarity", "jargon",
        "be careful", "make sure", "mindful",
        "metaphor", "figure of speech",
    ]
    for kw in ai_moderate_keywords:
        if kw in lower:
            return "ai_moderate", f"AI can sometimes detect ({kw})"

    return "manual", "Requires human editorial judgment"


def extract_rules_locally(filename: str, section_title: str, content: str) -> list:
    """Extract rules from text using heuristic pattern matching."""
    if len(content.strip()) < 30:
        return []

    category, subcategory = _detect_category(filename)
    lines = content.split("\n")
    rules = []
    rule_counter = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not _is_rule_line(stripped):
            continue

        # Clean up the rule text
        rule_text = re.sub(r'^[-–—•]\s*', '', stripped)
        rule_text = re.sub(r'^\d+[\.\)]\s*', '', rule_text)
        rule_text = rule_text.strip()

        if len(rule_text) < 15 or len(rule_text) > 500:
            continue

        rule_counter += 1
        automatable, auto_notes = _classify_automation(rule_text)
        examples = _extract_examples(lines, i)

        rules.append(ExtractedRule(
            rule_id=f"{category}.{subcategory}.{rule_counter}",
            category=category,
            subcategory=subcategory,
            rule=rule_text,
            examples=examples,
            exceptions=[],
            source={"document": filename, "section": section_title},
            automatable=automatable,
            automation_notes=auto_notes,
        ))

    return rules


def detect_discrepancies_locally(rules: list) -> list:
    """Detect discrepancies using local heuristics (no API needed)."""
    discrepancies = []

    # Group rules by subcategory to find potential conflicts
    by_subcat = {}
    for r in rules:
        key = r.subcategory
        if key not in by_subcat:
            by_subcat[key] = []
        by_subcat[key].append(r)

    # Check 1: Look for contradictory keywords — only very specific pairs
    # and only across different source documents (same doc is usually consistent)
    contradiction_pairs = [
        ("serial comma", "no serial comma"),
        ("active voice", "passive voice"),
        ("u.s. english", "british english"),
        ("capitalize", "do not capitalize"),
        ("italicize", "do not italicize"),
    ]
    seen_conflicts = set()
    for subcat, subcat_rules in by_subcat.items():
        for r1 in subcat_rules:
            for r2 in subcat_rules:
                if r1.rule_id >= r2.rule_id:
                    continue
                # Only flag cross-document conflicts
                if r1.source.get("document") == r2.source.get("document"):
                    continue
                for pos_word, neg_word in contradiction_pairs:
                    r1_lower = r1.rule.lower()
                    r2_lower = r2.rule.lower()
                    conflict_key = (pos_word, r1.source.get("document"), r2.source.get("document"))
                    if conflict_key in seen_conflicts:
                        continue
                    if (pos_word in r1_lower and neg_word in r2_lower) or \
                       (neg_word in r1_lower and pos_word in r2_lower):
                        seen_conflicts.add(conflict_key)
                        discrepancies.append(Discrepancy(
                            type="conflict",
                            severity="medium",
                            title=f"Potential conflict in {subcat} rules",
                            description=f'Rule "{r1.rule[:80]}..." and rule "{r2.rule[:80]}..." may contradict each other regarding {pos_word}/{neg_word}.',
                            affected_rules=[r1.rule_id, r2.rule_id],
                            recommendation="Review these two rules and clarify which takes precedence.",
                        ))

    # Check 2: Common gaps — areas that style guides usually cover
    covered_topics = set()
    for r in rules:
        lower = r.rule.lower()
        if "abbreviat" in lower or "acronym" in lower:
            covered_topics.add("acronyms")
        if "reference" in lower or "citation" in lower:
            covered_topics.add("references")
        if "heading" in lower or "subhead" in lower:
            covered_topics.add("headings")
        if "abstract" in lower:
            covered_topics.add("abstract")
        if "figure" in lower or "table" in lower:
            covered_topics.add("figures_tables")
        if "italic" in lower:
            covered_topics.add("italics")
        if "number" in lower or "numeral" in lower:
            covered_topics.add("numbers")
        if "spelling" in lower:
            covered_topics.add("spelling")
        if "punctuation" in lower or "comma" in lower or "colon" in lower:
            covered_topics.add("punctuation")
        if "unit" in lower or "metric" in lower:
            covered_topics.add("units")
        if "data avail" in lower or "supplementary" in lower:
            covered_topics.add("data_availability")
        if "conflict" in lower or "competing" in lower:
            covered_topics.add("competing_interests")
        if "inclusive" in lower or "nonsexist" in lower or "bias" in lower:
            covered_topics.add("inclusive_language")
        if "keyword" in lower:
            covered_topics.add("keywords")

    expected_topics = {
        "acronyms": "Acronym/abbreviation handling rules",
        "references": "Reference and citation formatting",
        "headings": "Heading hierarchy and formatting",
        "abstract": "Abstract structure and constraints",
        "figures_tables": "Figure and table formatting",
        "numbers": "Number formatting (words vs. numerals)",
        "spelling": "Spelling preferences and exceptions",
        "punctuation": "Punctuation rules",
        "units": "Units of measurement",
        "data_availability": "Data availability statement requirements",
        "competing_interests": "Competing interests disclosure",
        "inclusive_language": "Inclusive/non-biased language guidelines",
        "keywords": "Keyword requirements",
    }

    for topic, description in expected_topics.items():
        if topic not in covered_topics:
            discrepancies.append(Discrepancy(
                type="gap",
                severity="low",
                title=f"No explicit rules for: {description}",
                description=f"Most publisher style guides include rules about {description}, but this was not found in the analyzed documents.",
                affected_rules=[],
                recommendation=f"Consider adding explicit guidelines for {description}.",
            ))

    # Check 3: Vague/ambiguous rules — only flag the most impactful ones
    vague_indicators = [
        "as appropriate", "at the editor's discretion",
        "it depends", "in some cases",
    ]
    ambiguity_count = 0
    max_ambiguities = 10  # cap to keep report useful
    for r in rules:
        if ambiguity_count >= max_ambiguities:
            break
        lower = r.rule.lower()
        for indicator in vague_indicators:
            if indicator in lower:
                ambiguity_count += 1
                discrepancies.append(Discrepancy(
                    type="ambiguity",
                    severity="low",
                    title=f"Ambiguous rule: '{indicator}' in {r.subcategory}",
                    description=f'Rule "{r.rule[:100]}..." uses the phrase "{indicator}" which may lead to inconsistent application.',
                    affected_rules=[r.rule_id],
                    recommendation=f"Consider making this rule more specific by defining when '{indicator}' applies.",
                ))
                break

    # Check 4: Duplicate/overlapping rules (same topic from different source files)
    seen_rule_hashes = {}
    for r in rules:
        # Simple similarity: first 40 chars of lowered rule
        key = r.rule.lower()[:40]
        if key in seen_rule_hashes:
            other = seen_rule_hashes[key]
            if other.source.get("document") != r.source.get("document"):
                discrepancies.append(Discrepancy(
                    type="overlap",
                    severity="low",
                    title=f"Duplicate rule across documents",
                    description=f'Similar rule found in "{other.source.get("document")}" and "{r.source.get("document")}": "{r.rule[:80]}..."',
                    affected_rules=[other.rule_id, r.rule_id],
                    recommendation="Consolidate into a single authoritative rule to avoid confusion.",
                ))
        else:
            seen_rule_hashes[key] = r

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    discrepancies.sort(key=lambda d: severity_order.get(d.severity, 2))

    return discrepancies


def rules_to_dict(rules: list) -> list:
    return [asdict(r) for r in rules]


def discrepancies_to_dict(discs: list) -> list:
    return [asdict(d) for d in discs]
