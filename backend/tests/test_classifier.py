import json

import pytest

from models.span import ClassifiedSpan, RawSpan
from pipeline.classifier import classify_spans


@pytest.mark.slow
def test_returns_status_and_fallacy_type():
    spans = [RawSpan(text="Everyone knows vaccines cause autism.", start=0, end=36)]
    result = classify_spans(spans)
    assert len(result) == 1
    assert isinstance(result[0], ClassifiedSpan)
    assert result[0].status in ("confirmed", "possibly")
    assert result[0].fallacy_type
    assert isinstance(result[0].confidence, float)


@pytest.mark.slow
def test_preserves_original_keys():
    spans = [RawSpan(text="All politicians lie.", start=0, end=20)]
    result = classify_spans(spans)
    assert result[0].start == 0
    assert result[0].end == 20


def test_threshold_determines_status(monkeypatch):
    import types

    import numpy as np

    fake_model = types.SimpleNamespace(
        encode=lambda texts, **kw: np.array([[1.0] * 768], dtype="float32")
    )
    fake_index = types.SimpleNamespace(
        search=lambda emb, k: (np.array([[0.85]], dtype="float32"), np.array([[0]]))
    )
    fake_labels = ["ad populum"]

    from pipeline import classifier
    monkeypatch.setattr(classifier, "_load_resources", lambda: (fake_model, fake_index, fake_labels))

    result = classifier.classify_spans([RawSpan(text="x", start=0, end=1)])
    assert result[0].status == "confirmed"
    assert result[0].fallacy_type == "ad populum"

    # Below threshold
    fake_index2 = types.SimpleNamespace(
        search=lambda emb, k: (np.array([[0.75]], dtype="float32"), np.array([[0]]))
    )
    monkeypatch.setattr(classifier, "_load_resources", lambda: (fake_model, fake_index2, fake_labels))
    result2 = classifier.classify_spans([RawSpan(text="x", start=0, end=1)])
    assert result2[0].status == "possibly"


# Helper for sidecar tests: stub out the heavy SentenceTransformer/faiss loads
# so we exercise only the metadata read+verify path. We seed _SENTINEL_SLOT with
# a callable that returns a fake (model, index, labels) triple. `d` and
# `ntotal` mirror the FAISS Index attributes consulted by the verifier.
def _stub_heavy_loads(monkeypatch, classifier_mod, *, dim: int = 768, ntotal: int = 1):
    import types

    fake_model = types.SimpleNamespace(encode=lambda *a, **k: None)
    fake_index = types.SimpleNamespace(search=lambda *a, **k: None, d=dim, ntotal=ntotal)
    fake_labels = ["x"]

    def fake_st(*args, **kwargs):
        return fake_model

    def fake_read_index(_path):
        return fake_index

    monkeypatch.setattr(classifier_mod, "SentenceTransformer", fake_st)
    monkeypatch.setattr(classifier_mod.faiss, "read_index", fake_read_index)
    return fake_model, fake_index, fake_labels


def test_load_resources_warns_when_sidecar_missing(monkeypatch, tmp_path):
    from pipeline import classifier

    classifier._load_resources.cache_clear()

    (tmp_path / "logical_fallacy.index").write_bytes(b"")
    (tmp_path / "logical_fallacy_labels.json").write_text(json.dumps(["x"]))
    # NOTE: no sidecar file written

    monkeypatch.setattr(classifier, "DATA_DIR", tmp_path)
    _stub_heavy_loads(monkeypatch, classifier)

    with pytest.warns(UserWarning, match="meta.json"):
        classifier._load_resources()
    classifier._load_resources.cache_clear()


def test_load_resources_raises_on_embedder_mismatch(monkeypatch, tmp_path):
    from pipeline import classifier

    classifier._load_resources.cache_clear()

    (tmp_path / "logical_fallacy.index").write_bytes(b"")
    (tmp_path / "logical_fallacy_labels.json").write_text(json.dumps(["x"]))
    (tmp_path / "logical_fallacy.index.meta.json").write_text(json.dumps({
        "embedder_model": "some-other-embedder",
        "embedder_library_version": "0.0.0",
        "embedder_revision": classifier.MPNET_REVISION,
        "embedding_dim": 768,
        "vector_count": 1,
    }))

    monkeypatch.setattr(classifier, "DATA_DIR", tmp_path)
    _stub_heavy_loads(monkeypatch, classifier)

    with pytest.raises(RuntimeError, match="some-other-embedder"):
        classifier._load_resources()
    classifier._load_resources.cache_clear()


def test_load_resources_raises_on_embedder_revision_mismatch(monkeypatch, tmp_path):
    from pipeline import classifier

    classifier._load_resources.cache_clear()

    (tmp_path / "logical_fallacy.index").write_bytes(b"")
    (tmp_path / "logical_fallacy_labels.json").write_text(json.dumps(["x"]))
    (tmp_path / "logical_fallacy.index.meta.json").write_text(json.dumps({
        "embedder_model": classifier.EMBEDDER_MODEL,
        "embedder_library_version": "5.4.1",
        "embedder_revision": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        "embedding_dim": 768,
        "vector_count": 1,
    }))

    monkeypatch.setattr(classifier, "DATA_DIR", tmp_path)
    _stub_heavy_loads(monkeypatch, classifier)

    with pytest.raises(RuntimeError, match="revision"):
        classifier._load_resources()
    classifier._load_resources.cache_clear()


def test_load_resources_accepts_sidecar_without_revision(monkeypatch, tmp_path):
    # Backward-compat: an older sidecar (pre-revision) should not block startup
    # — only a sidecar that *declares* a revision must match.
    from pipeline import classifier

    classifier._load_resources.cache_clear()

    (tmp_path / "logical_fallacy.index").write_bytes(b"")
    (tmp_path / "logical_fallacy_labels.json").write_text(json.dumps(["x"]))
    (tmp_path / "logical_fallacy.index.meta.json").write_text(json.dumps({
        "embedder_model": classifier.EMBEDDER_MODEL,
        "embedder_library_version": "5.4.1",
        "embedding_dim": 768,
        "vector_count": 1,
    }))

    monkeypatch.setattr(classifier, "DATA_DIR", tmp_path)
    _stub_heavy_loads(monkeypatch, classifier)

    _model, _index, labels = classifier._load_resources()
    assert labels == ["x"]
    classifier._load_resources.cache_clear()


def test_load_resources_raises_on_embedding_dim_mismatch(monkeypatch, tmp_path):
    from pipeline import classifier

    classifier._load_resources.cache_clear()

    (tmp_path / "logical_fallacy.index").write_bytes(b"")
    (tmp_path / "logical_fallacy_labels.json").write_text(json.dumps(["x"]))
    (tmp_path / "logical_fallacy.index.meta.json").write_text(json.dumps({
        "embedder_model": classifier.EMBEDDER_MODEL,
        "embedder_library_version": "5.4.1",
        "embedder_revision": classifier.MPNET_REVISION,
        "embedding_dim": 384,  # mismatch: stub reports d=768
        "vector_count": 1,
    }))

    monkeypatch.setattr(classifier, "DATA_DIR", tmp_path)
    _stub_heavy_loads(monkeypatch, classifier, dim=768, ntotal=1)

    with pytest.raises(RuntimeError, match="embedding_dim"):
        classifier._load_resources()
    classifier._load_resources.cache_clear()


def test_load_resources_raises_on_vector_count_mismatch(monkeypatch, tmp_path):
    from pipeline import classifier

    classifier._load_resources.cache_clear()

    (tmp_path / "logical_fallacy.index").write_bytes(b"")
    (tmp_path / "logical_fallacy_labels.json").write_text(json.dumps(["x"]))
    (tmp_path / "logical_fallacy.index.meta.json").write_text(json.dumps({
        "embedder_model": classifier.EMBEDDER_MODEL,
        "embedder_library_version": "5.4.1",
        "embedder_revision": classifier.MPNET_REVISION,
        "embedding_dim": 768,
        "vector_count": 999,  # mismatch: stub reports ntotal=1
    }))

    monkeypatch.setattr(classifier, "DATA_DIR", tmp_path)
    _stub_heavy_loads(monkeypatch, classifier, dim=768, ntotal=1)

    with pytest.raises(RuntimeError, match="vector_count"):
        classifier._load_resources()
    classifier._load_resources.cache_clear()


def test_load_resources_accepts_matching_sidecar(monkeypatch, tmp_path):
    from pipeline import classifier

    classifier._load_resources.cache_clear()

    (tmp_path / "logical_fallacy.index").write_bytes(b"")
    (tmp_path / "logical_fallacy_labels.json").write_text(json.dumps(["x"]))
    (tmp_path / "logical_fallacy.index.meta.json").write_text(json.dumps({
        "embedder_model": classifier.EMBEDDER_MODEL,
        "embedder_library_version": "5.4.1",
        "embedder_revision": classifier.MPNET_REVISION,
        "embedding_dim": 768,
        "vector_count": 1,
    }))

    monkeypatch.setattr(classifier, "DATA_DIR", tmp_path)
    _stub_heavy_loads(monkeypatch, classifier, dim=768, ntotal=1)

    _model, _index, labels = classifier._load_resources()
    assert labels == ["x"]
    classifier._load_resources.cache_clear()
