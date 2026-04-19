import logging
from functools import lru_cache
from typing import NamedTuple

import spacy
import torch
from transformers import pipeline as hf_pipeline

logger = logging.getLogger(__name__)


class SegmentationResult(NamedTuple):
    spans: list[dict]
    sentence_count: int


@lru_cache(maxsize=1)
def _nlp():
    return spacy.load("en_core_web_sm")

@lru_cache(maxsize=1)
def _arg_classifier():
    device = 0 if torch.cuda.is_available() else -1
    logger.info("roberta-argument device: %s", "cuda:0" if device == 0 else "cpu")
    return hf_pipeline(
        "text-classification",
        model="chkla/roberta-argument",
        device=device,
    )

def get_argument_spans(text: str) -> SegmentationResult:
    if not text.strip():
        return SegmentationResult([], 0)
    doc = _nlp()(text)
    sentences = list(doc.sents)
    if not sentences:
        return SegmentationResult([], 0)
    texts = [s.text for s in sentences]
    labels = _arg_classifier()(texts, batch_size=16, truncation=True)
    # chkla/roberta-argument outputs "ARGUMENT" / "NON-ARGUMENT".
    # transformers stubs type the pipeline return as a broad union (incl. None);
    # at runtime it's a list[dict[str, str]] when called with a list of strings.
    spans = [
        {"text": sent.text, "start": sent.start_char, "end": sent.end_char}
        for sent, label in zip(sentences, labels, strict=True)
        if label["label"] == "ARGUMENT"
    ]
    return SegmentationResult(spans, len(sentences))
