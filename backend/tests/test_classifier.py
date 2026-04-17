import pytest
from pipeline.classifier import classify_spans

pytestmark = pytest.mark.slow


def test_returns_status_and_fallacy_type():
    spans = [{"text": "Everyone knows vaccines cause autism.", "start": 0, "end": 36}]
    result = classify_spans(spans)
    assert len(result) == 1
    assert result[0]["status"] in ("confirmed", "possibly")
    assert "fallacy_type" in result[0]
    assert "confidence" in result[0]


def test_preserves_original_keys():
    spans = [{"text": "All politicians lie.", "start": 0, "end": 20}]
    result = classify_spans(spans)
    assert result[0]["start"] == 0
    assert result[0]["end"] == 20
