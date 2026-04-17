from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class Resolution(str, Enum):
    PENDING   = "PENDING"
    CONFIRMED = "CONFIRMED"
    CLEARED   = "CLEARED"
    MOOT      = "MOOT"
    DORMANT   = "DORMANT"

@dataclass
class Span:
    id: str
    status: str
    resolution: Resolution = Resolution.PENDING

@dataclass
class DependencyRule:
    source_id: str
    dependent_id: str
    when: str
    effect: str
    reason: str

class FallacyCollection:
    def __init__(self, spans: list[Span], rules: list[DependencyRule]):
        self.spans: dict[str, Span] = {s.id: s for s in spans}
        self.rules = rules

    def resolve(self, span_id: str, outcome: Resolution) -> list[tuple[str, Resolution, str]]:
        self.spans[span_id].resolution = outcome
        cascades = []
        for rule in self.rules:
            if rule.source_id == span_id and rule.when == outcome.value:
                dep = self.spans[rule.dependent_id]
                new_res = Resolution.MOOT if rule.effect == "moot" else Resolution.PENDING
                dep.resolution = new_res
                cascades.append((rule.dependent_id, new_res, rule.reason))
        return cascades

    def preview_cascade(self, span_id: str, outcome: Resolution) -> list[tuple[str, Resolution, str]]:
        return [
            (r.dependent_id,
             Resolution.MOOT if r.effect == "moot" else Resolution.PENDING,
             r.reason)
            for r in self.rules
            if r.source_id == span_id and r.when == outcome.value
        ]

    def active(self) -> list[Span]:
        return [s for s in self.spans.values()
                if s.resolution not in (Resolution.MOOT, Resolution.DORMANT)]

    def pending(self) -> list[Span]:
        return [s for s in self.spans.values() if s.resolution == Resolution.PENDING]

    def is_complete(self) -> bool:
        return all(s.resolution != Resolution.PENDING for s in self.spans.values())
