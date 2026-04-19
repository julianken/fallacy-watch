import pytest

from pipeline.segmenter import (
    ROBERTA_ARGUMENT_REVISION,
    SegmentationResult,
    get_argument_spans,
)


def test_roberta_argument_revision_is_pinned():
    # 40-char hex sha guarantees we never accidentally fall back to "main"
    # (which would make the segmenter silently track upstream HEAD).
    assert isinstance(ROBERTA_ARGUMENT_REVISION, str)
    assert len(ROBERTA_ARGUMENT_REVISION) == 40
    assert all(c in "0123456789abcdef" for c in ROBERTA_ARGUMENT_REVISION)


def test_arg_classifier_passes_revision_to_hf_pipeline(monkeypatch):
    captured = {}

    def fake_pipeline(*args, **kwargs):
        captured["kwargs"] = kwargs
        return lambda *a, **k: []

    from pipeline import segmenter

    segmenter._arg_classifier.cache_clear()
    monkeypatch.setattr(segmenter, "hf_pipeline", fake_pipeline)
    segmenter._arg_classifier()
    segmenter._arg_classifier.cache_clear()

    assert captured["kwargs"].get("revision") == ROBERTA_ARGUMENT_REVISION
    assert captured["kwargs"].get("model") == "chkla/roberta-argument"


ARGUMENTATIVE = "Taxes are theft and the government has no right to take your money."
NON_ARG = "The weather in Paris is often mild in spring."


@pytest.mark.slow
def test_returns_segmentation_result():
    from models.span import RawSpan

    result = get_argument_spans(ARGUMENTATIVE)
    assert isinstance(result, SegmentationResult)
    assert isinstance(result.spans, list)
    assert all(isinstance(s, RawSpan) for s in result.spans)
    assert isinstance(result.sentence_count, int)

@pytest.mark.slow
def test_argumentative_sentence_included():
    result = get_argument_spans(ARGUMENTATIVE)
    assert any(ARGUMENTATIVE[:20] in s.text for s in result.spans)

@pytest.mark.slow
def test_span_has_required_fields():
    result = get_argument_spans(ARGUMENTATIVE)
    assert len(result.spans) > 0
    span = result.spans[0]
    assert isinstance(span.text, str)
    assert isinstance(span.start, int)
    assert isinstance(span.end, int)

@pytest.mark.slow
def test_empty_text_returns_empty():
    result = get_argument_spans("")
    assert result.spans == []
    assert result.sentence_count == 0

@pytest.mark.slow
def test_sentence_count_matches_segmenter_pass():
    result = get_argument_spans("Sentence one. Sentence two. Sentence three.")
    assert result.sentence_count == 3
