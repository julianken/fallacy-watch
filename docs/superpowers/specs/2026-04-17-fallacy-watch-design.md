# fallacy-watch — Design Spec

**Date:** 2026-04-17

## Overview

A web app that analyzes any text for informal and formal argument fallacies. Users paste text, click Analyze, and get inline highlights with explanation cards. Ambiguous cases are surfaced as interactive challenges — the user resolves them, not a second LLM call.

---

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Input | Any text | General-purpose — articles, debates, social media, transcripts |
| UI | Web app | Inline highlights + explanation cards below annotated text |
| Interaction | Analyze on submit | Explicit, predictable, no real-time complexity |
| Fallacy scope | All categories | Relevance, weak induction, presumption, ambiguity, formal, propaganda |
| Ambiguous cases | User-resolved | Human judgment beats a second LLM call; more educational |
| LLM | GPT-4o mini | Content generation only — never classifies |
| Stack | FastAPI + React | Challenge flow is local state; HTMX requires server roundtrips per step |

---

## Architecture

### Analysis pipeline

```
spaCy
  → sentence segmentation

roberta-argument (local, in-process)
  → filter to argument spans only
  → non-argument sentences never reach fallacy detection

sentence-transformers + MAFALDA vector store (local, in-process)
  → embed spans, cosine similarity search
  → confidence >= 0.82 → status: confirmed
  → confidence <  0.82 → status: possibly, fallacy_type: best_guess

GPT-4o mini (single batched call, external network)
  → receives all spans with assigned fallacy_type
  → generates: explanation, challenge, if_legitimate, if_fallacy, dependency_rules
  → never reclassifies — only explains
  → system prompt is cached across calls
```

### FastAPI endpoint

```
POST /analyze
  Request:  { text: str, max_chars: int = 20_000 }
  Response: { spans: SpanResult[], rules: DependencyRule[], meta: AnalysisMeta }
```

### SpanResult schema

```
SpanResult {
  id:                str
  text:              str
  start:             int          # character offset
  end:               int
  status:            "confirmed" | "possibly"
  fallacy_type:      str
  explanation:       str
  challenge:         Challenge
  if_legitimate:     str | None   # possibly cards only
  if_fallacy:        str | None   # possibly cards only
  content_generated: bool         # False if LLM step failed
}
```

### FallacyCollection

Python class that owns span state and dependency cascade logic. Serialized to JSON for React.

```
FallacyCollection {
  spans: dict[id → Span]
  rules: list[DependencyRule]

  resolve(id, outcome) → cascades: list[(id, Resolution, reason)]
  active()             → Span[]
  pending()            → Span[]
  preview_cascade(id, outcome) → list[(id, Resolution, reason)]
  is_complete()        → bool
}

DependencyRule {
  source_id:    str
  dependent_id: str
  when:         Resolution        # CONFIRMED | CLEARED
  effect:       "moot" | "activate"
  reason:       str               # shown to user when cascade fires
}
```

**Resolution states:** PENDING · CONFIRMED · CLEARED · MOOT · DORMANT

---

## Challenge type system

Each fallacy type maps to one challenge template. The challenge targets the logical structure of the fallacy, not the truth of the claim.

| Challenge type | Fallacy types | Core question |
|---|---|---|
| `counterexample` | Hasty generalization, false cause | Can you name one instance that breaks the universal claim? (counterexample exists → fallacy confirmed) |
| `domain_check` | Appeal to authority | Does the authority's expertise cover this specific claim? |
| `meaning_check` | Equivocation, amphiboly | Is the key word used with the same meaning throughout? |
| `representation_check` | Straw man | Is this a fair characterization of the original position? |
| `non_sequitur` | Red herring, false dichotomy | Does the conclusion actually follow from the premise? |
| `premise_check` | Ad populum, begging the question | Is this established, or is the consensus/premise being asserted without support? |

---

## Dependency rules

When one span's challenge is only meaningful if another span's premise holds, the pipeline infers a dependency. GPT-4o mini returns `dependency_rules` as part of its JSON response — it sees all spans and the full text, giving it enough context to identify sequential logical relationships.

**Cascade behaviour:**
- Source confirmed → dependent goes MOOT ("premise failed — argument collapsed at step one")
- Source cleared → dependent activates from DORMANT ("premise granted — now test the connection")
- Independent fallacies (no sequential logic) → no dependency rule, both cards remain active

Users can always expand a MOOT card via "Review anyway →".

---

## React component tree

```
<App>                          holds text + collection state
  ├── <TextInput>               textarea + Analyze button
  ├── <AnnotatedText>           text split by character offsets into plain/highlighted segments
  │     └── <Highlight>         color = fallacy_type, dashed border = possibly, muted = moot
  └── <FindingsList>            ordered by position in text
        ├── <ConfirmedCard>     explanation + challenge
        ├── <PossiblyCard>      if_legitimate / if_fallacy side-by-side + challenge
        └── <MootCard>          collapsed, shows cascade reason + "Review anyway →"
```

**`useFallacyCollection` hook** — mirrors Python `FallacyCollection.resolve()` in JS. Holds all resolution state locally. No server roundtrips after initial `/analyze` response.

---

## Error handling

| Failure | Response |
|---|---|
| Text empty / too long | 422 — never reaches pipeline |
| No argument spans found | 200 with empty spans[] — React shows "no arguments detected" |
| GPT-4o mini timeout / 500 | Retry once → degrade to template challenge content, `content_generated: false` |
| GPT-4o mini 429 (rate limit) | Exponential backoff × 3 → same degradation |
| Malformed LLM JSON | Retry with stricter prompt → same degradation |

**Template fallback** — when `content_generated: false`, React renders a generic challenge based on `challenge_type`. The card is visually marked as degraded. All resolution logic still works normally.

---

## Cost model

~5 argument spans flagged per 1,000-word document after local filtering. GPT-4o mini is called once per analysis with all spans batched — not once per span.

| Step | Cost |
|---|---|
| spaCy + roberta-argument + sentence-transformers | $0.00 (local) |
| GPT-4o mini (all spans batched, content generation only) | ~$0.00047/doc |
| Per 1,000 documents | ~$0.47 |

**Note:** The `0.82` confidence threshold for confirmed vs. possibly is a tunable starting point — adjust based on false positive rate during testing.
