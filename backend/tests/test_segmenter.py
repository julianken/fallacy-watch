import pytest

pytestmark = pytest.mark.slow

from pipeline.segmenter import SegmentationResult, get_argument_spans  # noqa: E402

ARGUMENTATIVE = "Taxes are theft and the government has no right to take your money."
NON_ARG = "The weather in Paris is often mild in spring."

def test_returns_segmentation_result():
    result = get_argument_spans(ARGUMENTATIVE)
    assert isinstance(result, SegmentationResult)
    assert isinstance(result.spans, list)
    assert isinstance(result.sentence_count, int)

def test_argumentative_sentence_included():
    result = get_argument_spans(ARGUMENTATIVE)
    assert any(ARGUMENTATIVE[:20] in s["text"] for s in result.spans)

def test_span_has_required_keys():
    result = get_argument_spans(ARGUMENTATIVE)
    assert len(result.spans) > 0
    assert {"text", "start", "end"} <= result.spans[0].keys()

def test_empty_text_returns_empty():
    result = get_argument_spans("")
    assert result.spans == []
    assert result.sentence_count == 0

def test_sentence_count_matches_segmenter_pass():
    result = get_argument_spans("Sentence one. Sentence two. Sentence three.")
    assert result.sentence_count == 3
