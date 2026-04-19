_MAP: dict[str, str] = {
    "faulty generalization":  "counterexample",
    "false causality":        "counterexample",
    "fallacy of credibility": "domain_check",
    "equivocation":           "meaning_check",
    "fallacy of extension":   "representation_check",
    "fallacy of logic":       "non_sequitur",
    "fallacy of relevance":   "non_sequitur",
    "false dilemma":          "non_sequitur",
    "ad hominem":             "non_sequitur",
    "intentional":            "non_sequitur",
    "miscellaneous":          "non_sequitur",  # defensive: not in current labels but safe forward-compat guard
    "ad populum":             "premise_check",
    "appeal to emotion":      "premise_check",
    "circular reasoning":     "premise_check",
}

def challenge_type_for(fallacy_type: str) -> str:
    return _MAP.get(fallacy_type.lower(), "non_sequitur")
