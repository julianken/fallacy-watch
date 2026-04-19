import os

# Skip the lifespan model warmup in tests — the suite mocks the heavy pipeline
# functions, so loading mpnet/FAISS/spaCy/roberta-argument on every collection
# would burn tens of seconds without exercising real code. Set before main is
# imported (FastAPI evaluates lifespan when the app starts under AsyncClient).
os.environ.setdefault("ANALYZE_SKIP_WARMUP", "1")
