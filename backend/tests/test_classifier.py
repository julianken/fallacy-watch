import pytest
from pipeline.classifier import classify_spans


@pytest.mark.slow
def test_returns_status_and_fallacy_type():
    spans = [{"text": "Everyone knows vaccines cause autism.", "start": 0, "end": 36}]
    result = classify_spans(spans)
    assert len(result) == 1
    assert result[0]["status"] in ("confirmed", "possibly")
    assert "fallacy_type" in result[0]
    assert "confidence" in result[0]


@pytest.mark.slow
def test_preserves_original_keys():
    spans = [{"text": "All politicians lie.", "start": 0, "end": 20}]
    result = classify_spans(spans)
    assert result[0]["start"] == 0
    assert result[0]["end"] == 20


def test_threshold_determines_status(monkeypatch):
    import numpy as np
    import types

    fake_model = types.SimpleNamespace(
        encode=lambda texts, **kw: np.array([[1.0] * 768], dtype="float32")
    )
    fake_index = types.SimpleNamespace(
        search=lambda emb, k: (np.array([[0.85]], dtype="float32"), np.array([[0]]))
    )
    fake_labels = ["ad populum"]

    from pipeline import classifier
    monkeypatch.setattr(classifier, "_load_resources", lambda: (fake_model, fake_index, fake_labels))

    result = classifier.classify_spans([{"text": "x", "start": 0, "end": 1}])
    assert result[0]["status"] == "confirmed"
    assert result[0]["fallacy_type"] == "ad populum"

    # Below threshold
    fake_index2 = types.SimpleNamespace(
        search=lambda emb, k: (np.array([[0.75]], dtype="float32"), np.array([[0]]))
    )
    monkeypatch.setattr(classifier, "_load_resources", lambda: (fake_model, fake_index2, fake_labels))
    result2 = classifier.classify_spans([{"text": "x", "start": 0, "end": 1}])
    assert result2[0]["status"] == "possibly"
