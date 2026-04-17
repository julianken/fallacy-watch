import json
import pathlib
import numpy as np
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import faiss

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
CONFIDENCE_THRESHOLD = 0.82


@lru_cache(maxsize=1)
def _load_resources():
    model = SentenceTransformer("all-mpnet-base-v2")
    index = faiss.read_index(str(DATA_DIR / "logical_fallacy.index"))
    labels = json.loads((DATA_DIR / "logical_fallacy_labels.json").read_text())
    return model, index, labels


def classify_spans(spans: list[dict]) -> list[dict]:
    if not spans:
        return []
    model, index, labels = _load_resources()
    embeddings = model.encode(
        [s["text"] for s in spans], batch_size=32, normalize_embeddings=True
    )
    embeddings = np.array(embeddings, dtype="float32")
    distances, indices = index.search(embeddings, k=1)
    result = []
    for span, dist, idx in zip(spans, distances, indices):
        confidence = float(dist[0])
        result.append({
            **span,
            "fallacy_type": labels[int(idx[0])],
            "confidence": confidence,
            "status": "confirmed" if confidence >= CONFIDENCE_THRESHOLD else "possibly",
        })
    return result
