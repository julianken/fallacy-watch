import json
import logging
import pathlib
import warnings
from functools import lru_cache

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from models.span import ClassifiedSpan, RawSpan

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


def _verify_index_metadata(index: faiss.Index) -> None:
    # Sidecar is written by data/build_index.py. Each check catches a different
    # silent-degradation failure mode:
    # - embedder_model: different sentence-transformer family with the same
    #   dimension would still produce nearest neighbors with no error.
    # - embedder_revision: same family but a different upstream commit; weights
    #   shift, query embeddings drift apart from indexed ones. Only enforced
    #   when the sidecar declares one (older sidecars predate the field).
    # - embedding_dim: must match the FAISS index dimension or .search() fails
    #   with a cryptic shape error, not a clear classifier-config diagnostic.
    # - vector_count: rebuilt-but-not-shipped index is the most common dev
    #   gotcha; sidecar may be ahead of the .index file (or vice versa).
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

    indexed_revision = meta.get("embedder_revision")
    if indexed_revision is not None and indexed_revision != MPNET_REVISION:
        raise RuntimeError(
            f"FAISS index was built with embedder revision "
            f"{indexed_revision!r} but classifier pins {MPNET_REVISION!r}. "
            f"Rebuild the index: python data/build_index.py"
        )

    indexed_dim = meta.get("embedding_dim")
    if indexed_dim is not None and indexed_dim != index.d:
        raise RuntimeError(
            f"FAISS index sidecar declares embedding_dim={indexed_dim} but "
            f"the loaded index reports dim={index.d}. Rebuild the index: "
            f"python data/build_index.py"
        )

    indexed_count = meta.get("vector_count")
    if indexed_count is not None and indexed_count != index.ntotal:
        raise RuntimeError(
            f"FAISS index sidecar declares vector_count={indexed_count} but "
            f"the loaded index reports ntotal={index.ntotal}. Rebuild the "
            f"index: python data/build_index.py"
        )


@lru_cache(maxsize=1)
def _load_resources():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("sentence-transformers device: %s", device)
    model = SentenceTransformer(EMBEDDER_MODEL, device=device, revision=MPNET_REVISION)
    index = faiss.read_index(str(DATA_DIR / "logical_fallacy.index"))
    _verify_index_metadata(index)
    labels = json.loads((DATA_DIR / "logical_fallacy_labels.json").read_text())
    return model, index, labels


def classify_spans(spans: list[RawSpan]) -> list[ClassifiedSpan]:
    if not spans:
        return []
    model, index, labels = _load_resources()
    embeddings = model.encode(
        [s.text for s in spans], batch_size=32, normalize_embeddings=True
    )
    embeddings = np.array(embeddings, dtype="float32")
    distances, indices = index.search(embeddings, k=1)
    result: list[ClassifiedSpan] = []
    for span, dist, idx in zip(spans, distances, indices, strict=True):
        confidence = float(dist[0])
        result.append(ClassifiedSpan(
            **span.model_dump(),
            fallacy_type=labels[int(idx[0])],
            confidence=confidence,
            status="confirmed" if confidence >= CONFIDENCE_THRESHOLD else "possibly",
        ))
    return result
