# fallacy-watch

A web app that analyzes text for argument fallacies. Users paste text, click Analyze, and get inline highlights with explanation cards. Ambiguous cases surface as interactive challenges — the user resolves them, not a second LLM call.

## Project structure

```
backend/        FastAPI app + NLP pipeline (Python 3.11+)
frontend/       React 18 + TypeScript + Vite
docs/
  specs/        Design spec
  plans/        Implementation plan
```

## Running the app

**Backend** (from `backend/`):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload --port 8000
```

**Frontend** (from `frontend/`):
```bash
npm install
npm run dev        # http://localhost:5173 — proxies /analyze to :8000
```

## Running tests

**Backend:**
```bash
cd backend
source .venv/bin/activate
pytest -v
```

**Frontend:**
```bash
cd frontend
npx vitest run
```

### Pre-release checks

CI runs `pytest -v -m "not slow"` — the `slow` marker is reserved for tests
that hit external services (real OpenAI API). Before cutting a release, run
the slow tier locally to catch contract drift between our `ExplainerOutput`
schema and OpenAI structured outputs:

```bash
cd backend
source .venv/bin/activate
OPENAI_API_KEY=sk-... pytest -v -m slow tests/test_explainer.py
```

Tests gated by `@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), ...)`
auto-skip when the key is absent, so the same command is safe in any
environment.

## Environment variables

```
OPENAI_API_KEY=<your key>             # required for GPT-4o mini explainer step
ANALYZE_MAX_CONCURRENT=2              # optional: bounded semaphore on /analyze ML inference
ANALYZE_RATE_LIMIT=10/minute          # optional: per-IP slowapi rate limit on /analyze
ANALYZE_SKIP_WARMUP=1                 # optional: skip lifespan model warmup (used by tests)
EXPLAINER_MAX_PAYLOAD_CHARS=50000     # optional: max chars in OpenAI prompt before fallback
EXPLAINER_MAX_OUTPUT_TOKENS=2000      # optional: max output tokens for OpenAI parse call
```

Copy `.env.example` to `.env` in `backend/` and fill in your key. The app degrades gracefully (template fallback content) if the key is missing or the API call fails.

`/analyze` rate limiting is in-memory (per-process) via slowapi — fine for a single uvicorn worker. Multi-worker deployments should configure a shared backend (Redis) or move rate limiting to the reverse proxy.

## Key architecture decisions

- **Local models only for classification**: spaCy (segmentation) → roberta-argument (argument filter) → sentence-transformers + FAISS (fallacy classification). No external calls for classification.
- **GPT-4o mini for content only**: A single batched call generates explanations, challenges, and dependency rules. It never reclassifies.
- **Confidence threshold 0.82**: Spans above this are `confirmed`; below are `possibly`. Adjust in `backend/pipeline/classifier.py`.
- **No server roundtrips after /analyze**: All resolution state lives in the React `useFallacyCollection` hook.
- **FallacyCollection cascade logic**: Defined in `backend/models/collection.py` (Python) and mirrored in `frontend/src/hooks/useFallacyCollection.ts` (TypeScript). Keep them in sync.

## Build the logical-fallacy index (one-time)

```bash
cd backend
source .venv/bin/activate
python data/build_index.py
```

Outputs three files in `backend/data/`:
- `logical_fallacy.index` — the FAISS vector store
- `logical_fallacy_labels.json` — parallel label list
- `logical_fallacy.index.meta.json` — sidecar with embedder name/version/SHA + dim + count

Commit all three. The classifier reads the sidecar at startup and refuses to load if `embedder_model` doesn't match, catching the silent-degradation case where the index was built with a different mpnet checkpoint than the loader instantiates.

## Code conventions

- Python: no type: ignore, strict Pydantic v2 models, pytest with asyncio_mode=auto
- TypeScript: strict mode, no `any`, Vitest for tests
- No comments explaining what the code does — only comments explaining non-obvious WHY
- TDD: write failing test first, implement to pass, then commit

### Type-checking (pyright)

`pyright` runs in CI with `typeCheckingMode = "standard"` (config in `backend/pyproject.toml`). Standard, not `strict`, because spaCy/transformers/faiss ship limited stubs and `strict` would force noise-suppression at every third-party boundary. Tighten to `strict` once stubs improve or once we wrap external libs in typed adapters. `# pyright: ignore[<rule>]` comments must include a one-line justification (no bare ignores).
