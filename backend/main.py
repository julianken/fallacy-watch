import time
from functools import lru_cache
import spacy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.span import (
    AnalyzeRequest, AnalyzeResponse, SpanResult,
    Challenge, Question, ChallengeType, DependencyRule, AnalysisMeta,
)
from pipeline.segmenter import get_argument_spans
from pipeline.classifier import classify_spans
from pipeline.explainer import generate_content

@lru_cache(maxsize=1)
def _nlp():
    return spacy.load("en_core_web_sm")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")

    t0 = time.monotonic()
    text = req.text[: req.max_chars]

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
        ch = c.challenge if c else None
        spans_out.append(SpanResult(
            id=sid,
            text=span["text"],
            start=span["start"],
            end=span["end"],
            status=span["status"],
            fallacy_type=span["fallacy_type"],
            explanation=c.explanation if c else "",
            challenge=Challenge(
                type=ChallengeType(ch.type if ch else "non_sequitur"),
                question=Question(
                    text=ch.question.text if ch else "",
                    yes_label=ch.question.yes_label if ch else "Yes",
                    no_label=ch.question.no_label if ch else "No",
                ),
            ),
            if_legitimate=c.if_legitimate if c else None,
            if_fallacy=c.if_fallacy if c else None,
            content_generated=c is not None,
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
            fallacy_count=len(spans_out),
            processing_ms=ms,
        ),
    )
