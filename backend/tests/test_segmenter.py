import pytest

pytestmark = pytest.mark.slow

from pipeline.segmenter import get_argument_spans  # noqa: E402

ARGUMENTATIVE = "Taxes are theft and the government has no right to take your money."
NON_ARG = "The weather in Paris is often mild in spring."

def test_returns_list():
    assert isinstance(get_argument_spans(ARGUMENTATIVE), list)

def test_argumentative_sentence_included():
    spans = get_argument_spans(ARGUMENTATIVE)
    assert any(ARGUMENTATIVE[:20] in s["text"] for s in spans)

def test_span_has_required_keys():
    spans = get_argument_spans(ARGUMENTATIVE)
    assert len(spans) > 0
    assert {"text", "start", "end"} <= spans[0].keys()

def test_empty_text_returns_empty():
    assert get_argument_spans("") == []
