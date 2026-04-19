from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class ChallengeType(StrEnum):
    COUNTEREXAMPLE       = "counterexample"
    DOMAIN_CHECK         = "domain_check"
    MEANING_CHECK        = "meaning_check"
    REPRESENTATION_CHECK = "representation_check"
    NON_SEQUITUR         = "non_sequitur"
    PREMISE_CHECK        = "premise_check"

# --- Internal pipeline models (not on the wire) ---

class RawSpan(BaseModel):
    """Output of the segmenter — sentence text with character offsets."""
    text: str
    start: int
    end: int

class ClassifiedSpan(RawSpan):
    """Output of the classifier — a RawSpan plus its assigned fallacy_type,
    confidence score, and confirmation status. `id` is set by main.py after
    classification, before passing to the explainer."""
    id: str | None = None
    fallacy_type: str
    confidence: float
    status: Literal["confirmed", "possibly"]


class IdentifiedClassifiedSpan(RawSpan):
    """A ClassifiedSpan that has been stamped with an `id` by main.py.

    Mirrors ClassifiedSpan's fields but with `id: str` required, so pyright
    can statically catch callers that try to pass an unstamped span into the
    post-stamp pipeline (the explainer + fallback path) — replacing a runtime
    `assert span.id is not None` with a static guarantee.

    Defined as a sibling of ClassifiedSpan rather than a subclass because
    pyright treats Pydantic field overrides as mutable-and-invariant: a
    `str | None = None` parent field cannot be narrowed to `str` in a child
    without raising reportIncompatibleVariableOverride. Sibling models avoid
    that constraint.
    """
    id: str
    fallacy_type: str
    confidence: float
    status: Literal["confirmed", "possibly"]

class Question(BaseModel):
    text: str
    yes_label: str
    no_label: str

class Challenge(BaseModel):
    type: ChallengeType
    question: Question

class DependencyRule(BaseModel):
    source_id: str
    dependent_id: str
    when: Literal["CONFIRMED", "CLEARED"]
    effect: Literal["moot"]
    reason: str

class SpanResult(BaseModel):
    id: str
    text: str
    start: int
    end: int
    status: str     # "confirmed" | "possibly"
    fallacy_type: str
    explanation: str
    challenge: Challenge
    if_legitimate: str | None = None
    if_fallacy: str | None = None
    content_generated: bool = True

class AnalysisMeta(BaseModel):
    sentence_count: int
    argument_span_count: int
    fallacy_count: int
    processing_ms: int
    truncated: bool = False
    original_char_count: int | None = None

# Absolute server-side cap on /analyze input. A request larger than this is
# rejected at the schema layer before the server allocates the full payload —
# this is the cheap DoS guard. max_chars (below) is the soft cap that controls
# truncation after acceptance.
_HARD_MAX_TEXT_CHARS = 100_000

class AnalyzeRequest(BaseModel):
    text: str = Field(..., max_length=_HARD_MAX_TEXT_CHARS, min_length=1)
    max_chars: int = Field(default=20_000, gt=0, le=_HARD_MAX_TEXT_CHARS)

class AnalyzeResponse(BaseModel):
    spans: list[SpanResult]
    rules: list[DependencyRule]
    meta: AnalysisMeta

# --- Structured output models for GPT-4o mini (beta.parse) ---

class ExplainerQuestion(BaseModel):
    text: str
    yes_label: str
    no_label: str

class ExplainerChallenge(BaseModel):
    type: Literal["counterexample","domain_check","meaning_check",
                  "representation_check","non_sequitur","premise_check"]
    question: ExplainerQuestion

class ExplainerDependencyRule(BaseModel):
    source_id: str
    dependent_id: str
    when: Literal["CONFIRMED", "CLEARED"]
    effect: Literal["moot"]
    reason: str

class ExplainerSpan(BaseModel):
    id: str
    explanation: str
    challenge: ExplainerChallenge
    if_legitimate: str | None = None
    if_fallacy: str | None = None

class ExplainerOutput(BaseModel):
    spans: list[ExplainerSpan]
    dependency_rules: list[ExplainerDependencyRule]
