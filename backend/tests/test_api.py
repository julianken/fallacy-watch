from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from models.span import ExplainerOutput, ExplainerSpan, ExplainerChallenge, ExplainerQuestion

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

async def test_analyze_returns_spans():
    from main import app
    with (patch("main.get_argument_spans", return_value=MOCK_SEGMENTS),
          patch("main.classify_spans", return_value=MOCK_CLASSIFIED),
          patch("main.generate_content", return_value=_mock_explainer_output())):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            resp = await c.post("/analyze", json={"text": "All scientists lie."})
    assert resp.status_code == 200
    assert resp.json()["spans"][0]["fallacy_type"] == "Faulty Generalization"

async def test_analyze_empty_text_returns_422():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        resp = await c.post("/analyze", json={"text": ""})
    assert resp.status_code == 422

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
