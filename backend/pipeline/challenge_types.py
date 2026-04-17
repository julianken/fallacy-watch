_MAP: dict[str, str] = {
    "Faulty Generalization":  "counterexample",
    "False Causality":        "counterexample",
    "Fallacy of Credibility": "domain_check",
    "Equivocation":           "meaning_check",
    "Fallacy of Extension":   "representation_check",
    "Fallacy of Logic":       "non_sequitur",
    "Fallacy of Relevance":   "non_sequitur",
    "False Dilemma":          "non_sequitur",
    "Ad Hominem":             "non_sequitur",
    "Intentional":            "non_sequitur",
    "Miscellaneous":          "non_sequitur",
    "Ad Populum":             "premise_check",
    "Appeal to Emotion":      "premise_check",
    "Circular Reasoning":     "premise_check",
}

def challenge_type_for(fallacy_type: str) -> str:
    return _MAP.get(fallacy_type, "non_sequitur")
