import os

import pytest

# Skip the lifespan model warmup in tests — the suite mocks the heavy pipeline
# functions, so loading mpnet/FAISS/spaCy/roberta-argument on every collection
# would burn tens of seconds without exercising real code. Set before main is
# imported (FastAPI evaluates lifespan when the app starts under AsyncClient).
os.environ.setdefault("ANALYZE_SKIP_WARMUP", "1")

# Use a small per-IP rate limit so the rate-limit test can trigger 429 quickly.
# Other tests issue at most 1-2 requests each, well under the cap.
os.environ.setdefault("ANALYZE_RATE_LIMIT", "3/minute")


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    # slowapi's in-memory storage persists across tests within a process and
    # all tests use the same default client IP (127.0.0.1). Reset the limiter
    # state before every test so they don't poison each other.
    from main import app
    storage = app.state.limiter._storage
    if hasattr(storage, "storage"):
        storage.storage.clear()
    yield
