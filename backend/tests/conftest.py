import json
import os
import pathlib

import pytest

# Skip the lifespan model warmup in tests — the suite mocks the heavy pipeline
# functions, so loading mpnet/FAISS/spaCy/roberta-argument on every collection
# would burn tens of seconds without exercising real code. Set before main is
# imported (FastAPI evaluates lifespan when the app starts under AsyncClient).
os.environ.setdefault("ANALYZE_SKIP_WARMUP", "1")

# Use a small per-IP rate limit so the rate-limit test can trigger 429 quickly.
# Other tests issue at most 1-2 requests each, well under the cap.
os.environ.setdefault("ANALYZE_RATE_LIMIT", "3/minute")

# Canonical lowercase fallacy labels emitted by the real classifier. Source of
# truth for any test that needs a fallacy_type string — drift between fixtures
# and the labels file becomes a test-time error, not a silent prod bug.
FALLACY_LABELS: list[str] = sorted(set(json.loads(
    (pathlib.Path(__file__).parent.parent / "data" / "logical_fallacy_labels.json").read_text()
)))


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    # slowapi's in-memory storage persists across tests within a process and
    # all tests use the same default client IP (127.0.0.1). Reset the limiter
    # state before every test so they don't poison each other. Use the public
    # Limiter.reset() rather than reaching into ._storage.storage — the
    # in-memory backend also tracks expirations/events/locks beside the
    # counter dict, and a moving-window strategy uses different state
    # entirely. Limiter.reset() delegates to the storage's own reset(), which
    # clears all of those in one shot.
    from main import app
    app.state.limiter.reset()
    yield
