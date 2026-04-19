import json
import pathlib

import faiss
import numpy as np
import sentence_transformers
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

from pipeline.classifier import EMBEDDER_MODEL, MPNET_REVISION

DATA_DIR = pathlib.Path(__file__).parent


def build():
    print("Loading tasksource/logical-fallacy...")
    ds = load_dataset("tasksource/logical-fallacy", split="train")
    print("Column names:", ds.column_names)

    # Probe actual column names
    text_col = "source_article" if "source_article" in ds.column_names else ds.column_names[0]
    if "label" in ds.column_names:
        label_col = "label"
    elif "logical_fallacies" in ds.column_names:
        label_col = "logical_fallacies"
    else:
        label_col = "fallacy_type"
    texts = ds[text_col]

    # Resolve labels to strings; some versions store integer IDs, others strings
    raw_labels = ds[label_col]
    if raw_labels and isinstance(raw_labels[0], int):
        label_names = ds.features[label_col].names
        labels = [label_names[i] for i in raw_labels]
    else:
        labels = [str(lbl) for lbl in raw_labels]

    print(f"Encoding {len(texts)} examples with text_col={text_col!r}, label_col={label_col!r}...")
    model = SentenceTransformer(EMBEDDER_MODEL, revision=MPNET_REVISION)
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        normalize_embeddings=True,
    )
    embeddings = np.array(embeddings, dtype="float32")

    print("Building FAISS index...")
    index = faiss.IndexFlatIP(embeddings.shape[1])
    # faiss has no type stubs; .add(x) signature is inferred incorrectly
    index.add(embeddings)  # pyright: ignore[reportCallIssue]

    faiss.write_index(index, str(DATA_DIR / "logical_fallacy.index"))
    (DATA_DIR / "logical_fallacy_labels.json").write_text(json.dumps(labels))
    # Sidecar lets the loader catch silent embedder/index drift — a regenerated
    # index with a different mpnet checkpoint still has dim 768, so without
    # this metadata FAISS would happily return degraded nearest neighbors.
    meta = {
        "embedder_model": EMBEDDER_MODEL,
        "embedder_library_version": sentence_transformers.__version__,
        "embedder_revision": MPNET_REVISION,
        "embedding_dim": int(embeddings.shape[1]),
        "vector_count": int(index.ntotal),
    }
    (DATA_DIR / "logical_fallacy.index.meta.json").write_text(
        json.dumps(meta, indent=2) + "\n"
    )
    print(f"Done. {index.ntotal} vectors. Labels sample: {labels[:3]}")
    print(f"Wrote sidecar metadata: {meta}")


if __name__ == "__main__":
    build()
