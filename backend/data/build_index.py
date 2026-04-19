import json
import pathlib

import faiss
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

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
    model = SentenceTransformer("all-mpnet-base-v2")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        normalize_embeddings=True,
    )
    embeddings = np.array(embeddings, dtype="float32")

    print("Building FAISS index...")
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(DATA_DIR / "logical_fallacy.index"))
    (DATA_DIR / "logical_fallacy_labels.json").write_text(json.dumps(labels))
    print(f"Done. {index.ntotal} vectors. Labels sample: {labels[:3]}")


if __name__ == "__main__":
    build()
