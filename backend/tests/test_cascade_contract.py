import json
import pathlib

import pytest

from models.collection import DependencyRule, FallacyCollection, Resolution, Span

# Shared golden fixtures live OUTSIDE backend/ so the TypeScript hook can read
# the same files. Drift between the two implementations becomes a test-time
# error in whichever language regressed.
FIXTURES = pathlib.Path(__file__).parent.parent.parent / "fixtures" / "cascade-contract"


@pytest.mark.parametrize(
    "fixture_path",
    sorted(FIXTURES.glob("*.json")),
    ids=lambda p: p.stem,
)
def test_cascade_matches_fixture(fixture_path: pathlib.Path) -> None:
    fx = json.loads(fixture_path.read_text())
    spans = [Span(id=s["id"], status=s["status"]) for s in fx["spans"]]
    rules = [DependencyRule(**r) for r in fx["rules"]]
    coll = FallacyCollection(spans, rules)
    for action in fx["actions"]:
        coll.resolve(action["resolve"], Resolution(action["outcome"]))
    actual = {sid: span.resolution.value for sid, span in coll.spans.items()}
    assert actual == fx["expected_final_state"]
