import json
import logging
import os
from openai import OpenAI
from models.span import (ExplainerOutput, ExplainerSpan, ExplainerChallenge,
                          ExplainerQuestion)
from pipeline.challenge_types import challenge_type_for

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a fallacy explanation engine. For each span you receive a text excerpt
and an assigned fallacy_type. Generate:
- explanation: what the fallacy is and why this specific span was flagged (2-3 sentences)
- challenge: targeted question to help the user decide if it's really a fallacy
  - type: one of counterexample|domain_check|meaning_check|representation_check|non_sequitur|premise_check
  - question.text, question.yes_label, question.no_label
  - For counterexample: yes_label confirms the fallacy (counterexample exists → fallacy confirmed)
- if_legitimate: one sentence — what this looks like if the argument is valid
- if_fallacy: one sentence — what this looks like if it is a fallacy

Also return dependency_rules if any span's challenge only makes sense after another's resolution.
Never reclassify the assigned fallacy_type."""

_TEMPLATE_QUESTIONS = {
    "counterexample":       ("Can you name a single instance that disproves this universal claim?",
                             "Counterexample exists → fallacy confirmed",
                             "No counterexample → not confirmed"),
    "domain_check":         ("Does this authority's expertise cover this specific claim?",
                             "Outside their domain → fallacy",
                             "Expertise is relevant → not a fallacy"),
    "meaning_check":        ("Is the key term used with the same meaning throughout?",
                             "Meaning shifts → fallacy",
                             "Consistent meaning → not a fallacy"),
    "representation_check": ("Is this a fair characterization of the original position?",
                             "Misrepresents it → fallacy",
                             "Fair representation → not a fallacy"),
    "non_sequitur":         ("Does this conclusion actually follow from the premise?",
                             "Doesn't follow → fallacy",
                             "Follows logically → not a fallacy"),
    "premise_check":        ("Is this premise established, or simply asserted?",
                             "Not established → fallacy",
                             "Well established → not a fallacy"),
}

def _fallback_content(spans: list[dict]) -> ExplainerOutput:
    result_spans = []
    for span in spans:
        ct = challenge_type_for(span["fallacy_type"])
        q_text, yes_lbl, no_lbl = _TEMPLATE_QUESTIONS[ct]
        result_spans.append(ExplainerSpan(
            id=span["id"],
            explanation=f"Possibly a {span['fallacy_type']}.",
            challenge=ExplainerChallenge(
                type=ct,
                question=ExplainerQuestion(text=q_text, yes_label=yes_lbl, no_label=no_lbl),
            ),
            if_legitimate=None,
            if_fallacy=None,
        ))
    return ExplainerOutput(spans=result_spans, dependency_rules=[])

def generate_content(
    spans: list[dict],
    full_text: str,
    client: OpenAI | None = None,
) -> ExplainerOutput:
    if client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            return _fallback_content(spans)
        client = OpenAI(api_key=api_key, timeout=30.0)

    payload = json.dumps({"full_text": full_text, "spans": spans}, ensure_ascii=False)

    for attempt in range(2):
        try:
            response = client.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": payload},
                ],
                response_format=ExplainerOutput,
            )
            msg = response.choices[0].message
            if msg.refusal:
                raise ValueError(f"Model refused: {msg.refusal}")
            return msg.parsed
        except Exception as e:
            logger.warning("explainer attempt %d failed: %s", attempt, e, exc_info=True)
            if attempt == 1:
                return _fallback_content(spans)
    return _fallback_content(spans)
