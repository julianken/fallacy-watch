import pytest
from pydantic import BaseModel, ValidationError

from models.collection import DependencyRule, FallacyCollection, Resolution, Span


def _span(id, status="possibly"):
    return Span(id=id, status=status, resolution=Resolution.PENDING)


def test_span_and_dependency_rule_are_pydantic():
    assert issubclass(Span, BaseModel)
    assert issubclass(DependencyRule, BaseModel)


def test_dependency_rule_rejects_lowercase_when():
    with pytest.raises(ValidationError):
        DependencyRule(
            source_id="a",
            dependent_id="b",
            when="confirmed",
            effect="moot",
            reason="x",
        )


def test_dependency_rule_rejects_pending_when():
    with pytest.raises(ValidationError):
        DependencyRule(
            source_id="a",
            dependent_id="b",
            when="PENDING",
            effect="moot",
            reason="x",
        )

def test_resolve_confirmed_cascades_moot():
    col = FallacyCollection(
        spans=[_span("a"), _span("b")],
        rules=[DependencyRule(source_id="a", dependent_id="b",
                              when="CONFIRMED", effect="moot", reason="premise failed")]
    )
    cascades = col.resolve("a", Resolution.CONFIRMED)
    assert col.spans["b"].resolution == Resolution.MOOT
    assert cascades[0] == ("b", Resolution.MOOT, "premise failed")

def test_is_complete_false_when_pending():
    assert FallacyCollection(spans=[_span("a")], rules=[]).is_complete() is False

def test_is_complete_true_when_all_resolved():
    col = FallacyCollection(spans=[_span("a")], rules=[])
    col.resolve("a", Resolution.CONFIRMED)
    assert col.is_complete() is True

def test_active_excludes_moot():
    col = FallacyCollection(
        spans=[_span("a"), _span("b")],
        rules=[DependencyRule(source_id="a", dependent_id="b",
                              when="CONFIRMED", effect="moot", reason="x")]
    )
    col.resolve("a", Resolution.CONFIRMED)
    assert "b" not in [s.id for s in col.active()]

def test_preview_cascade_does_not_mutate():
    col = FallacyCollection(
        spans=[_span("a"), _span("b")],
        rules=[DependencyRule(source_id="a", dependent_id="b",
                              when="CONFIRMED", effect="moot", reason="x")]
    )
    col.preview_cascade("a", Resolution.CONFIRMED)
    assert col.spans["b"].resolution == Resolution.PENDING
