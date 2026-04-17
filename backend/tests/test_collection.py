from models.collection import FallacyCollection, Resolution, Span, DependencyRule

def _span(id, status="possibly"):
    return Span(id=id, status=status, resolution=Resolution.PENDING)

def test_resolve_confirmed_cascades_moot():
    col = FallacyCollection(
        spans=[_span("a"), _span("b")],
        rules=[DependencyRule(source_id="a", dependent_id="b",
                              when="CONFIRMED", effect="moot", reason="premise failed")]
    )
    cascades = col.resolve("a", Resolution.CONFIRMED)
    assert col.spans["b"].resolution == Resolution.MOOT
    assert cascades[0] == ("b", Resolution.MOOT, "premise failed")

def test_resolve_cleared_activates_dormant():
    b = Span(id="b", status="possibly", resolution=Resolution.DORMANT)
    col = FallacyCollection(
        spans=[_span("a"), b],
        rules=[DependencyRule(source_id="a", dependent_id="b",
                              when="CLEARED", effect="activate", reason="premise granted")]
    )
    col.resolve("a", Resolution.CLEARED)
    assert col.spans["b"].resolution == Resolution.PENDING

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
