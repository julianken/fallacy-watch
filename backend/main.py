import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.span import (
    AnalysisMeta,
    AnalyzeRequest,
    AnalyzeResponse,
    Challenge,
    ChallengeType,
    DependencyRule,
    Question,
    SpanResult,
)
from pipeline.classifier import classify_spans
from pipeline.explainer import _fallback_content, generate_content
from pipeline.segmenter import _nlp, get_argument_spans

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")

    t0 = time.monotonic()
    original_len = len(req.text)
    text = req.text[: req.max_chars]
    truncated = len(text) < original_len

    raw_spans = get_argument_spans(text)
    classified = classify_spans(raw_spans)
    for i, span in enumerate(classified):
        span["id"] = f"span_{i}"

    explainer_out = generate_content(classified, text)
    content_by_id = {s.id: s for s in explainer_out.spans}

    spans_out: list[SpanResult] = []
    for span in classified:
        sid = span["id"]
        c = content_by_id.get(sid)
        model_generated = c is not None
        if c is None:
            c = _fallback_content([span]).spans[0]
        ch = c.challenge
        spans_out.append(SpanResult(
            id=sid,
            text=span["text"],
            start=span["start"],
            end=span["end"],
            status=span["status"],
            fallacy_type=span["fallacy_type"],
            explanation=c.explanation,
            challenge=Challenge(
                type=ChallengeType(ch.type),
                question=Question(
                    text=ch.question.text,
                    yes_label=ch.question.yes_label,
                    no_label=ch.question.no_label,
                ),
            ),
            if_legitimate=c.if_legitimate,
            if_fallacy=c.if_fallacy,
            content_generated=model_generated,
        ))

    rules_out = [
        DependencyRule(
            source_id=r.source_id, dependent_id=r.dependent_id,
            when=r.when, effect=r.effect, reason=r.reason,
        )
        for r in explainer_out.dependency_rules
    ]

    ms = int((time.monotonic() - t0) * 1000)
    return AnalyzeResponse(
        spans=spans_out,
        rules=rules_out,
        meta=AnalysisMeta(
            sentence_count=len(list(_nlp()(text).sents)),
            argument_span_count=len(raw_spans),
            fallacy_count=sum(1 for s in spans_out if s.status == "confirmed"),
            processing_ms=ms,
            truncated=truncated,
            original_char_count=original_len if truncated else None,
        ),
    )
