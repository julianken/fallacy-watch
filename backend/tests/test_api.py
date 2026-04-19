from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from models.span import ExplainerChallenge, ExplainerOutput, ExplainerQuestion, ExplainerSpan


def _mock_explainer_output():
    return ExplainerOutput(
        spans=[ExplainerSpan(
            id="span_0",
            explanation="Universal claim.",
            challenge=ExplainerChallenge(
                type="counterexample",
                question=ExplainerQuestion(
                    text="Name a counterexample?",
                    yes_label="Exists → fallacy", no_label="None → not a fallacy"),
            ),
            if_legitimate="Backed by data.", if_fallacy="No evidence.",
        )],
        dependency_rules=[],
    )

MOCK_SEGMENTS = [{"text": "All scientists lie.", "start": 0, "end": 18}]
MOCK_CLASSIFIED = [{"text": "All scientists lie.", "start": 0, "end": 18,
                    "fallacy_type": "Faulty Generalization", "confidence": 0.91,
                    "status": "confirmed"}]

@pytest.mark.asyncio
async def test_analyze_returns_spans():
    from main import app
    with (patch("main.get_argument_spans", return_value=MOCK_SEGMENTS),
          patch("main.classify_spans", return_value=MOCK_CLASSIFIED),
          patch("main.generate_content", return_value=_mock_explainer_output())):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            resp = await c.post("/analyze", json={"text": "All scientists lie."})
    assert resp.status_code == 200
    assert resp.json()["spans"][0]["fallacy_type"] == "Faulty Generalization"

@pytest.mark.asyncio
async def test_analyze_empty_text_returns_422():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        resp = await c.post("/analyze", json={"text": ""})
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_analyze_no_spans_returns_empty():
    from main import app
    empty = ExplainerOutput(spans=[], dependency_rules=[])
    with (patch("main.get_argument_spans", return_value=[]),
          patch("main.classify_spans", return_value=[]),
          patch("main.generate_content", return_value=empty)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            resp = await c.post("/analyze", json={"text": "The sky is blue."})
    assert resp.status_code == 200
    assert resp.json()["spans"] == []


@pytest.mark.asyncio
async def test_analyze_meta_not_truncated_for_short_input():
    from main import app
    empty = ExplainerOutput(spans=[], dependency_rules=[])
    with (patch("main.get_argument_spans", return_value=[]),
          patch("main.classify_spans", return_value=[]),
          patch("main.generate_content", return_value=empty)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            resp = await c.post("/analyze", json={"text": "The sky is blue."})
    assert resp.status_code == 200
    meta = resp.json()["meta"]
    assert meta["truncated"] is False
    assert meta["original_char_count"] is None


@pytest.mark.asyncio
async def test_analyze_meta_marks_truncated_when_input_exceeds_max_chars():
    from main import app
    empty = ExplainerOutput(spans=[], dependency_rules=[])
    long_text = "x" * 60_000
    with (patch("main.get_argument_spans", return_value=[]),
          patch("main.classify_spans", return_value=[]),
          patch("main.generate_content", return_value=empty)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            resp = await c.post(
                "/analyze",
                json={"text": long_text, "max_chars": 20_000},
            )
    assert resp.status_code == 200
    meta = resp.json()["meta"]
    assert meta["truncated"] is True
    assert meta["original_char_count"] == 60_000


@pytest.mark.asyncio
async def test_analyze_rejects_text_exceeding_hard_cap():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        resp = await c.post("/analyze", json={"text": "x" * 100_001})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_analyze_rate_limits_after_threshold():
    # conftest sets ANALYZE_RATE_LIMIT=3/minute; the autouse fixture clears
    # the limiter state before this test runs.
    from main import app
    empty = ExplainerOutput(spans=[], dependency_rules=[])
    with (patch("main.get_argument_spans", return_value=[]),
          patch("main.classify_spans", return_value=[]),
          patch("main.generate_content", return_value=empty)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            statuses = [
                (await c.post("/analyze", json={"text": "Some text."})).status_code
                for _ in range(4)
            ]
    assert statuses[:3] == [200, 200, 200]
    assert statuses[3] == 429
