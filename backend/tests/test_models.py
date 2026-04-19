import pytest
from pydantic import ValidationError

from models.span import (
    AnalysisMeta,
    AnalyzeResponse,
    Challenge,
    ChallengeType,
    ClassifiedSpan,
    DependencyRule,
    Question,
    RawSpan,
    SpanResult,
)


def test_span_result_serializes():
    span = SpanResult(
        id="a", text="Everyone knows politicians lie", start=0, end=30,
        status="possibly", fallacy_type="Ad Populum",
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
        fallacy_type="Faulty Generalization",
        confidence=0.91,
        status="confirmed",
    )
    assert classified.id is None
    data = classified.model_dump()
    assert data["text"] == "All scientists lie."
    assert data["fallacy_type"] == "Faulty Generalization"
    assert data["status"] == "confirmed"

    # `status` is a Literal — anything else must be rejected at construction.
    with pytest.raises(ValidationError):
        ClassifiedSpan(
            text="x", start=0, end=1, fallacy_type="t", confidence=0.5, status="maybe",
        )
