from models.span import (
    ChallengeType, Question, Challenge,
    SpanResult, AnalysisMeta, AnalyzeResponse,
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
