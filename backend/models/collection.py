from __future__ import annotations

import logging
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Resolution(StrEnum):
    PENDING   = "PENDING"
    CONFIRMED = "CONFIRMED"
    CLEARED   = "CLEARED"
    MOOT      = "MOOT"

class Span(BaseModel):
    id: str
    status: str
    resolution: Resolution = Resolution.PENDING

class DependencyRule(BaseModel):
    source_id: str
    dependent_id: str
    when: Literal["CONFIRMED", "CLEARED"]
    effect: Literal["moot"]
    reason: str

class FallacyCollection:
    def __init__(self, spans: list[Span], rules: list[DependencyRule]):
        self.spans: dict[str, Span] = {s.id: s for s in spans}
        # Drop rules referencing unknown span IDs so a hallucinated LLM rule
        # can't KeyError mid-resolve and leave the collection in a partial state.
        valid_rules: list[DependencyRule] = []
        for r in rules:
            if r.source_id not in self.spans or r.dependent_id not in self.spans:
                logger.warning("dropping cascade rule with unknown id(s): %r", r)
                continue
            valid_rules.append(r)
        self.rules = valid_rules

    def resolve(self, span_id: str, outcome: Resolution) -> list[tuple[str, Resolution, str]]:
        self.spans[span_id].resolution = outcome
        cascades = []
        for rule in self.rules:
            if rule.source_id == span_id and rule.when == outcome.value:
                if rule.effect == "moot":
                    dep = self.spans[rule.dependent_id]
                    dep.resolution = Resolution.MOOT
                    cascades.append((rule.dependent_id, Resolution.MOOT, rule.reason))
        return cascades

    def preview_cascade(
        self, span_id: str, outcome: Resolution,
    ) -> list[tuple[str, Resolution, str]]:
        return [
            (r.dependent_id, Resolution.MOOT, r.reason)
            for r in self.rules
            if r.source_id == span_id and r.when == outcome.value and r.effect == "moot"
        ]

    def active(self) -> list[Span]:
        return [s for s in self.spans.values()
                if s.resolution != Resolution.MOOT]

    def pending(self) -> list[Span]:
        return [s for s in self.spans.values() if s.resolution == Resolution.PENDING]

    def is_complete(self) -> bool:
        return all(s.resolution != Resolution.PENDING for s in self.spans.values())
