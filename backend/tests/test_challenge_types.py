import pytest

from pipeline.challenge_types import challenge_type_for


@pytest.mark.parametrize("label,expected", [
    # 13 runtime labels (all lowercase, as produced by classifier.py)
    ("ad populum",             "premise_check"),
    ("appeal to emotion",      "premise_check"),
    ("circular reasoning",     "premise_check"),
    ("faulty generalization",  "counterexample"),
    ("false causality",        "counterexample"),
    ("fallacy of credibility", "domain_check"),
    ("equivocation",           "meaning_check"),
    ("fallacy of extension",   "representation_check"),
    ("fallacy of logic",       "non_sequitur"),
    ("fallacy of relevance",   "non_sequitur"),
    ("false dilemma",          "non_sequitur"),
    ("ad hominem",             "non_sequitur"),
    ("intentional",            "non_sequitur"),
    # 1 defensive entry (not a runtime label, kept for forward-compat)
    ("miscellaneous",          "non_sequitur"),
    # 1 synthetic default case — 13 runtime + 1 defensive + 1 unknown default = 15 total
    ("unknown label",          "non_sequitur"),
])
def test_challenge_type_for(label: str, expected: str) -> None:
    assert challenge_type_for(label) == expected
