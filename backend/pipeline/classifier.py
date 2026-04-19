import json
import logging
import pathlib
import warnings
from functools import lru_cache

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
CONFIDENCE_THRESHOLD = 0.82
EMBEDDER_MODEL = "all-mpnet-base-v2"

# Pin the HuggingFace embedder to a specific commit SHA. The FAISS index stores
# vectors produced by this exact checkpoint — if upstream republishes weights
# under the same name, dimension would still match but query embeddings would
# drift apart from the indexed ones, silently degrading classification.
#
# To upgrade: bump MPNET_REVISION, rebuild the FAISS index
# (`python data/build_index.py` writes a new sidecar with the new revision),
# commit the regenerated index + labels + sidecar, and re-run the tests.
MPNET_REVISION = "e8c3b32edf5434bc2275fc9bab85f82640a19130"

logger = logging.getLogger(__name__)


def _verify_index_metadata() -> None:
    # Sidecar is written by data/build_index.py. Asserting embedder_model
    # match catches the silent failure mode where the index was built with a
    # different sentence-transformer than the loader is about to instantiate
    # — dimensions would still match, FAISS would return nearest neighbors,
    # and classifications would quietly degrade with no error.
    meta_path = DATA_DIR / "logical_fallacy.index.meta.json"
    if not meta_path.exists():
        warnings.warn(
            "FAISS index has no .meta.json sidecar; cannot verify embedder "
            "compatibility. Rebuild with `python data/build_index.py` to "
            "enable this check.",
            stacklevel=3,
        )
        return
    meta = json.loads(meta_path.read_text())
    indexed_embedder = meta.get("embedder_model")
    if indexed_embedder != EMBEDDER_MODEL:
        raise RuntimeError(
            f"FAISS index was built with embedder {indexed_embedder!r} but "
            f"classifier loads {EMBEDDER_MODEL!r}. Rebuild the index: "
            f"python data/build_index.py"
        )


@lru_cache(maxsize=1)
def _load_resources():
    _verify_index_metadata()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("sentence-transformers device: %s", device)
    model = SentenceTransformer(EMBEDDER_MODEL, device=device, revision=MPNET_REVISION)
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
    for span, dist, idx in zip(spans, distances, indices, strict=True):
        confidence = float(dist[0])
        result.append({
            **span,
            "fallacy_type": labels[int(idx[0])],
            "confidence": confidence,
            "status": "confirmed" if confidence >= CONFIDENCE_THRESHOLD else "possibly",
        })
    return result
