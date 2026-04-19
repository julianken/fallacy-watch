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

## Environment variables

```
OPENAI_API_KEY=<your key>    # required for GPT-4o mini explainer step
```

Copy `.env.example` to `.env` in `backend/` and fill in your key. The app degrades gracefully (template fallback content) if the key is missing or the API call fails.

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

Outputs `backend/data/logical_fallacy.index` and `backend/data/logical_fallacy_labels.json`. Commit both.

## Code conventions

- Python: no type: ignore, strict Pydantic v2 models, pytest with asyncio_mode=auto
- TypeScript: strict mode, no `any`, Vitest for tests
- No comments explaining what the code does — only comments explaining non-obvious WHY
- TDD: write failing test first, implement to pass, then commit

### Type-checking (pyright)

`pyright` runs in CI with `typeCheckingMode = "standard"` (config in `backend/pyproject.toml`). Standard, not `strict`, because spaCy/transformers/faiss ship limited stubs and `strict` would force noise-suppression at every third-party boundary. Tighten to `strict` once stubs improve or once we wrap external libs in typed adapters. `# pyright: ignore[<rule>]` comments must include a one-line justification (no bare ignores).
