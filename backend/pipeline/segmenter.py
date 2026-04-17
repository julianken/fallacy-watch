import spacy
from transformers import pipeline as hf_pipeline
from functools import lru_cache

@lru_cache(maxsize=1)
def _nlp():
    return spacy.load("en_core_web_sm")

@lru_cache(maxsize=1)
def _arg_classifier():
    return hf_pipeline(
        "text-classification",
        model="chkla/roberta-argument",
        device=-1,
    )

def get_argument_spans(text: str) -> list[dict]:
    if not text.strip():
        return []
    doc = _nlp()(text)
    sentences = list(doc.sents)
    if not sentences:
        return []
    texts = [s.text for s in sentences]
    labels = _arg_classifier()(texts, batch_size=16, truncation=True)
    return [
        {"text": sent.text, "start": sent.start_char, "end": sent.end_char}
        for sent, label in zip(sentences, labels)
        if label["label"] == "ARGUMENT"   # chkla/roberta-argument outputs "ARGUMENT" / "NON-ARGUMENT"
    ]
