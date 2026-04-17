from unittest.mock import MagicMock
from pipeline.explainer import generate_content, _fallback_content

SPANS = [{
    "id": "a", "text": "Everyone knows politicians lie",
    "start": 0, "end": 30, "status": "possibly",
    "fallacy_type": "Ad Populum", "confidence": 0.71,
}]

def _mock_parsed():
    from models.span import (ExplainerOutput, ExplainerSpan, ExplainerChallenge,
                              ExplainerQuestion)
    return ExplainerOutput(
        spans=[ExplainerSpan(
            id="a", explanation="Invokes consensus without evidence.",
            challenge=ExplainerChallenge(
                type="premise_check",
                question=ExplainerQuestion(
                    text="Is this consensus established?",
                    yes_label="Not established → fallacy",
                    no_label="Consensus is real → not a fallacy",
                ),
            ),
            if_legitimate="Survey data shows 80% of voters...",
            if_fallacy="No evidence offered.",
        )],
        dependency_rules=[],
    )

def test_returns_enriched_output():
    mock_client = MagicMock()
    mock_client.beta.chat.completions.parse.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(parsed=_mock_parsed(), refusal=None))]
    )
    result = generate_content(SPANS, "Everyone knows politicians lie.", client=mock_client)
    assert result.spans[0].explanation == "Invokes consensus without evidence."
    assert result.dependency_rules == []

def test_fallback_returns_template_content():
    result = _fallback_content(SPANS)
    assert result.spans[0].id == "a"
    assert result.spans[0].explanation != ""
    assert result.dependency_rules == []

def test_retries_on_failure():
    mock_client = MagicMock()
    mock_client.beta.chat.completions.parse.side_effect = [
        Exception("timeout"),
        MagicMock(choices=[MagicMock(message=MagicMock(parsed=_mock_parsed(), refusal=None))])
    ]
    result = generate_content(SPANS, "text", client=mock_client)
    assert result.spans[0].explanation == "Invokes consensus without evidence."
    assert mock_client.beta.chat.completions.parse.call_count == 2
