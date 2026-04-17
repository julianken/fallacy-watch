from pipeline.challenge_types import challenge_type_for

def test_known_mappings():
    assert challenge_type_for("Faulty Generalization") == "counterexample"
    assert challenge_type_for("Fallacy of Credibility") == "domain_check"
    assert challenge_type_for("Equivocation") == "meaning_check"
    assert challenge_type_for("Fallacy of Extension") == "representation_check"
    assert challenge_type_for("False Dilemma") == "non_sequitur"
    assert challenge_type_for("Ad Populum") == "premise_check"

def test_unknown_type_returns_non_sequitur():
    assert challenge_type_for("unknown") == "non_sequitur"
