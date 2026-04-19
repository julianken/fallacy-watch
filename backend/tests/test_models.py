import pytest
from pydantic import ValidationError

from models.span import (
    AnalysisMeta,
    AnalyzeResponse,
    Challenge,
    ChallengeType,
    ClassifiedSpan,
    DependencyRule,
    IdentifiedClassifiedSpan,
    Question,
    RawSpan,
    SpanResult,
)


def test_span_result_serializes():
    span = SpanResult(
        id="a", text="Everyone knows politicians lie", start=0, end=30,
        status="possibly", fallacy_type="ad populum",
        explanation="Invokes consensus without evidence.",
        challenge=Challenge(
            type=ChallengeType.PREMISE_CHECK,
            question=Question(text="Is this consensus established?",
                              yes_label="Not established → fallacy",
                              no_label="Consensus is real → not a fallacy"),
        ),
        if_legitimate="The claim cites survey data...", if_fallacy="No evidence offered.",
        content_generated=True,
    )
    data = span.model_dump()
    assert data["status"] == "possibly"
    assert data["challenge"]["type"] == "premise_check"

def test_analyze_response_empty_spans():
    resp = AnalyzeResponse(spans=[], rules=[], meta=AnalysisMeta(
        sentence_count=3, argument_span_count=0, fallacy_count=0, processing_ms=42
    ))
    assert resp.spans == []

def test_dependency_rule_rejects_pending_when():
    with pytest.raises(ValidationError):
        DependencyRule(
            source_id="a",
            dependent_id="b",
            when="PENDING",
            effect="moot",
            reason="x",
        )

def test_dependency_rule_rejects_lowercase_when():
    with pytest.raises(ValidationError):
        DependencyRule(
            source_id="a",
            dependent_id="b",
            when="confirmed",
            effect="moot",
            reason="x",
        )

def test_raw_and_classified_span_construct_and_serialize():
    raw = RawSpan(text="All scientists lie.", start=0, end=18)
    classified = ClassifiedSpan(
        **raw.model_dump(),
        fallacy_type="faulty generalization",
        confidence=0.91,
        status="confirmed",
    )
    assert classified.id is None
    data = classified.model_dump()
    assert data["text"] == "All scientists lie."
    assert data["fallacy_type"] == "faulty generalization"
    assert data["status"] == "confirmed"

    # `status` is a Literal — anything else must be rejected at construction.
    with pytest.raises(ValidationError):
        ClassifiedSpan(
            text="x", start=0, end=1, fallacy_type="t", confidence=0.5, status="maybe",
        )


def test_identified_classified_span_requires_id():
    # Subclass tightens id from `str | None = None` to `str` so the post-stamp
    # pipeline (explainer + fallback) can rely on `.id` being non-None
    # statically rather than via a runtime assert.
    with pytest.raises(ValidationError):
        IdentifiedClassifiedSpan(
            text="x", start=0, end=1, fallacy_type="t", confidence=0.5, status="possibly",
        )

    span = IdentifiedClassifiedSpan(
        id="span_0", text="x", start=0, end=1,
        fallacy_type="t", confidence=0.5, status="possibly",
    )
    assert span.id == "span_0"


def test_fixture_fallacy_types_are_canonical():
    """Every fallacy_type used in test fixtures must appear in
    logical_fallacy_labels.json.

    conftest.FALLACY_LABELS exists to be the canonical source-of-truth for
    test fixtures. Without an enforcement test, a typo like "ad-populum"
    would only surface as a downstream silent mismatch. This test imports
    the test-module fixture spans directly and asserts every fallacy_type
    is in the canonical labels set.
    """
    from tests import test_api, test_explainer
    from tests.conftest import FALLACY_LABELS

    used = {s.fallacy_type for s in test_api.MOCK_CLASSIFIED}
    used |= {s.fallacy_type for s in test_explainer.SPANS}

    canonical = set(FALLACY_LABELS)
    drift = used - canonical
    assert not drift, (
        f"test fixtures use fallacy_type(s) {drift!r} not in "
        f"logical_fallacy_labels.json — fix the fixture or rebuild the index"
    )
