import re

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "not", "no", "if", "when",
    "that", "this", "it", "its", "as", "such", "which", "who", "use",
    "used", "using", "e.g", "i.e", "etc",
}

SIMILARITY_THRESHOLD = 0.72


def _tokenise(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9']+", text.lower())
    return {t for t in tokens if t not in STOP_WORDS and len(t) > 2}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def deduplicate_rules(rules: list[dict]) -> list[dict]:
    """
    Remove near-duplicate rules within a list.
    When two rules are similar, keep the one with the longer (more complete) text.
    Merge source references from the duplicate into the kept rule.
    Input rules: list of dicts with keys: rule, source_section, remarks, source_document
    """
    if not rules:
        return rules

    tokenised = [_tokenise(r["rule"]) for r in rules]
    keep = [True] * len(rules)

    for i in range(len(rules)):
        if not keep[i]:
            continue
        for j in range(i + 1, len(rules)):
            if not keep[j]:
                continue
            score = _jaccard(tokenised[i], tokenised[j])
            if score >= SIMILARITY_THRESHOLD:
                # Keep the longer (more complete) rule
                if len(rules[j]["rule"]) > len(rules[i]["rule"]):
                    # j is better — merge i's source into j, drop i
                    _merge_source(rules[j], rules[i])
                    keep[i] = False
                    break
                else:
                    # i is better — merge j's source into i, drop j
                    _merge_source(rules[i], rules[j])
                    keep[j] = False

    return [r for i, r in enumerate(rules) if keep[i]]


def _merge_source(keep_rule: dict, drop_rule: dict) -> None:
    keep_doc = keep_rule.get("source_document", "")
    drop_doc = drop_rule.get("source_document", "")
    if drop_doc and drop_doc not in keep_doc:
        keep_rule["source_document"] = f"{keep_doc}, {drop_doc}".strip(", ")


def deduplicate_session_rules(rules_by_category: dict[str, list[dict]]) -> dict[str, list[dict]]:
    return {
        category: deduplicate_rules(rules)
        for category, rules in rules_by_category.items()
    }
