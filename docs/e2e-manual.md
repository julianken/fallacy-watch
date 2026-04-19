# Manual E2E Tests — fallacy-watch

Step-by-step flows for a Claude agent using the Playwright MCP tools.
Run both servers before starting any test case.

## Prerequisites

```
# Terminal 1 — backend
cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev          # http://localhost:5173
```

**Tools used in these tests:**
- `browser_navigate` — go to a URL
- `browser_snapshot` — read current DOM/accessibility tree
- `browser_take_screenshot` — capture visual state
- `browser_fill` — fill a form field by label
- `browser_click` — click an element
- `browser_wait_for` — wait for text/selector to appear
- `browser_evaluate` — run JS expressions in the page

---

## TC-01 — Analyze button is disabled on empty textarea

**Goal:** Verify the Analyze button cannot be clicked when the textarea is empty.

1. `browser_navigate` to `http://localhost:5173`
2. `browser_snapshot` — confirm the page has loaded:
   - Title "fallacy-watch" is visible
   - Textarea with placeholder "Paste any text to analyze for argument fallacies..." is present
   - "Analyze →" button is present
3. `browser_evaluate` with expression `document.querySelector('button').disabled` — expect `true`
4. **Pass condition:** button has `disabled` attribute; no results section is visible.

---

## TC-02 — Happy path: text with fallacies produces annotated results

**Goal:** Full analysis cycle from input to visible findings.

**Sample text** (paste this exactly):
```
Everyone agrees this policy has failed, so it must be scrapped immediately.
Scientists who challenge mainstream climate science are just contrarians seeking
publicity. If we allow this small exception to the rule, soon there will be no
rules at all.
```

1. `browser_navigate` to `http://localhost:5173`
2. `browser_fill` textarea (label: `"Text to analyze for argument fallacies"`) with the sample text above
3. `browser_snapshot` — confirm the "Analyze →" button is now enabled (not disabled)
4. `browser_click` the "Analyze →" button
5. `browser_wait_for` text `"Analyzing…"` to appear (loading state — button label changes)
6. `browser_wait_for` text `"finding"` to appear — this is the `N findings · Xms` metadata line that signals results have rendered (timeout: 60 000 ms to allow for model inference)
7. `browser_snapshot` — confirm:
   - An annotated text block is visible above the findings list
   - At least one `<mark>` element (highlight) is rendered inside it
   - At least one card is visible below — either a `ConfirmedCard` ("Confirmed —") or `PossiblyCard` ("⚠ Possibly —")
   - The metadata line shows `N findings · Xms`
8. `browser_take_screenshot` — visual record of the initial results state
9. **Pass condition:** annotated text block and ≥1 finding card are visible; no error message is shown.

---

## TC-03 — Resolve a confirmed finding as CONFIRMED (user agrees it's a fallacy)

**Goal:** Clicking the YES challenge button on a `ConfirmedCard` transitions it to a red `ResolvedCard` and dims the inline highlight.

**Setup:** Complete TC-02 first. If no `ConfirmedCard` appeared (all findings are `PossiblyCard`), skip to TC-05.

1. `browser_snapshot` — locate a card that has the text "Confirmed —" in its header
2. Note the `yes_label` button text inside that card (e.g. "Counterexample exists → fallacy confirmed")
3. `browser_click` the red YES button inside that `ConfirmedCard`
4. `browser_snapshot` — confirm:
   - The card now shows a badge with text matching `"Confirmed — <fallacy_type>"` (red badge, `ResolvedCard`)
   - The challenge buttons are **gone** — no YES/NO buttons visible on that card
   - The card has reduced opacity (0.75)
5. `browser_evaluate` — verify no highlights are dimmed after a CONFIRMED resolution:
   ```js
   // CONFIRMED status keeps full color; only CLEARED/MOOT dim to 0.4
   // All visible marks should have opacity !== '0.4'
   [...document.querySelectorAll('mark')].every(m => m.style.opacity !== '0.4')
   ```
   Expect `true` — every remaining mark is still fully colored. Note: if no `<mark>` elements exist at all this also returns `true`; cross-check against step 7 snapshot to confirm marks are present.
6. `browser_take_screenshot`
7. **Pass condition:** `ConfirmedCard` is replaced by `ResolvedCard` with red "Confirmed —" badge; challenge buttons gone.

---

## TC-04 — Resolve a confirmed finding as CLEARED (user says it's not a fallacy)

**Goal:** Clicking the NO challenge button on a `ConfirmedCard` transitions it to a green `ResolvedCard` and dims the inline highlight.

**Setup:** Complete TC-02. If the previous test resolved a card, re-analyze (TC-11 covers reset) or use a second unresolved `ConfirmedCard`. Alternatively navigate fresh and re-analyze.

1. `browser_snapshot` — locate an unresolved `ConfirmedCard` (has challenge buttons)
2. Note the `no_label` button text (e.g. "No counterexample → not confirmed")
3. `browser_click` the green NO button inside that `ConfirmedCard`
4. `browser_snapshot` — confirm:
   - The card now shows a badge with text `"Cleared — not a fallacy"` (green badge, `ResolvedCard`)
   - Challenge buttons are gone
5. `browser_evaluate`:
   ```js
   // CLEARED highlights dim to opacity 0.4 — find the dimmed mark
   [...document.querySelectorAll('mark')].filter(m => m.style.opacity === '0.4').length
   ```
   Expect ≥ 1 (the CLEARED span's highlight is dimmed).
6. `browser_take_screenshot`
7. **Pass condition:** `ResolvedCard` shows green "Cleared — not a fallacy" badge; corresponding inline highlight is visually dimmed.

---

## TC-05 — Resolve a possibly finding as CONFIRMED

**Goal:** Clicking YES on a `PossiblyCard` (dashed yellow border) transitions it to a red `ResolvedCard`.

**Setup:** Complete TC-02. Requires at least one `PossiblyCard` in the results (dashed yellow border, "⚠ Possibly —" header).

1. `browser_snapshot` — locate a card with "⚠ Possibly —" in its header
2. Verify it shows a `LegitimacyComparison` section if `if_legitimate` and `if_fallacy` are present ("✓ IF LEGITIMATE" / "✗ IF A FALLACY" columns)
3. `browser_click` the red YES challenge button inside that `PossiblyCard`
4. `browser_snapshot` — confirm:
   - Card replaced by `ResolvedCard` with red "Confirmed —" badge
   - Dashed yellow border gone
   - Challenge buttons gone
5. **Pass condition:** `PossiblyCard` replaced by red `ResolvedCard`.

---

## TC-06 — Resolve a possibly finding as CLEARED

**Goal:** Clicking NO on a `PossiblyCard` transitions it to a green `ResolvedCard` and dims the highlight.

**Setup:** Complete TC-02. Requires a `PossiblyCard`.

1. `browser_snapshot` — locate a `PossiblyCard`
2. `browser_click` the green NO challenge button
3. `browser_snapshot` — confirm:
   - Card replaced by `ResolvedCard` with green "Cleared — not a fallacy" badge
4. `browser_evaluate`:
   ```js
   [...document.querySelectorAll('mark')].filter(m => m.style.opacity === '0.4').length
   ```
   Expect ≥ 1 (CLEARED highlight is dimmed).
5. **Pass condition:** `PossiblyCard` replaced by green `ResolvedCard`; inline highlight dimmed.

---

## TC-07 — Moot cascade: resolving one finding silences a dependent

**Goal:** When a source span is resolved and a `moot` dependency rule exists, the dependent span's card changes to a dimmed `MootCard`.

**Note:** This flow requires the backend to have returned a `dependency_rules` array with at least one `effect: "moot"` entry. Check the response before running.

**Setup:** Complete TC-02.

1. `browser_evaluate` to inspect the dependency rules:
   ```js
   // Read rules from the page — App stores result in React state; extract from rendered DOM instead
   // Count MootCards that appear after resolution to confirm cascade fired
   document.querySelectorAll('[id^="card-"]').length
   ```
   Note the total card count.

2. If no `MootCard` appeared immediately after TC-02 results loaded, discover the cascade source by resolving cards one at a time:
   - `browser_click` the YES or NO button on any unresolved card
   - `browser_wait_for` text `"MOOT —"` with timeout 5 000 ms
   - If `"MOOT —"` does not appear within 5 seconds, try the next unresolved card
   - Stop as soon as `"MOOT —"` appears — the card just resolved was the cascade source

3. If a `MootCard` appeared after the resolution:
   - `browser_snapshot` — confirm the `MootCard` is visible:
     - Header: "MOOT — `<fallacy_type>`"
     - Reason text is present (e.g. "resolved by cascade")
     - The card has reduced opacity (0.5)
     - A "Review anyway →" button is visible
   - `browser_evaluate`:
     ```js
     // Confirm the corresponding inline highlight is dimmed
     [...document.querySelectorAll('mark')].filter(m => m.style.opacity === '0.4').length
     ```
     Expect ≥ 1.

4. `browser_take_screenshot`
5. **Pass condition:** A `MootCard` is visible with cascade reason; inline highlight for that span is dimmed. If no `moot` rules were returned by this analysis run, mark as "N/A — no cascade rules in this response" and note it for re-test with different input text.

---

## TC-08 — "Review anyway" un-silences a MOOT card

**Goal:** Clicking "Review anyway →" on a `MootCard` replaces it with the full challenge card.

**Setup:** TC-07 must have produced a visible `MootCard`.

1. `browser_snapshot` — confirm `MootCard` is present with "Review anyway →" button
2. `browser_click` the "Review anyway →" button on the `MootCard`
3. `browser_snapshot` — confirm:
   - `MootCard` is **gone** for that span
   - A `ConfirmedCard` or `PossiblyCard` (matching `span.status`) now shows in its place with challenge buttons
4. `browser_evaluate` — verify the highlight opacity has been restored:
   ```js
   // After "Review anyway", the MOOT span returns to full opacity
   // Note: browser_snapshot accessibility trees do not expose inline styles —
   // this evaluate is the only way to verify opacity restoration
   [...document.querySelectorAll('mark')].filter(m => m.style.opacity === '0.4').length
   ```
   Expect 0 (no marks are dimmed — the previously-MOOT highlight is back to full color).
5. `browser_evaluate`:
   ```js
   document.querySelectorAll('button').length
   ```
   Should be higher than before (challenge buttons re-appeared).
6. **Pass condition:** `MootCard` is replaced by a challenge card; `browser_evaluate` confirms no marks are dimmed.

---

## TC-09 — Clicking an inline highlight scrolls to its finding card

**Goal:** Clicking a `<mark>` highlight in the annotated text panel scrolls the page to the corresponding finding card.

**Setup:** Complete TC-02 with ≥1 result visible. The annotated text panel must contain at least one `<mark>` element.

1. `browser_snapshot` — identify a `<mark>` element (role="button") in the annotated text block
2. `browser_evaluate` to get the target card's current scroll position:
   ```js
   const marks = document.querySelectorAll('mark[role="button"]')
   marks.length  // confirm at least one highlight exists
   ```
3. `browser_click` on one of the `<mark role="button">` elements in the annotated text
4. `browser_evaluate` to confirm the corresponding card is now in view:
   ```js
   // The card ID is card-{span.id}; check if it's visible in the viewport
   const cards = document.querySelectorAll('[id^="card-"]')
   const inView = [...cards].filter(el => {
     const r = el.getBoundingClientRect()
     return r.top >= 0 && r.bottom <= window.innerHeight
   })
   inView.length
   ```
   Expect ≥ 1 card is visible in viewport after clicking.
5. `browser_take_screenshot`
6. **Pass condition:** At least one finding card is fully visible in the viewport after clicking the highlight.

---

## TC-10 — Analysis of text with no argument spans

**Goal:** When no argument fallacies are detected, the app shows "No argument fallacies detected." and no annotated text block.

**Sample text** (factual, no argumentation):
```
The Eiffel Tower is located in Paris, France. It was built in 1889.
Water boils at 100 degrees Celsius at sea level. Paris is the capital of France.
```

1. `browser_navigate` to `http://localhost:5173`
2. `browser_fill` textarea with the factual sample text
3. `browser_click` "Analyze →"
4. `browser_wait_for` either `"No argument fallacies detected."` or `"finding"` — timeout: 60 000 ms
5. `browser_snapshot` — confirm:
   - "No argument fallacies detected." message is visible
   - No annotated text block is visible
   - No finding cards are visible
6. `browser_take_screenshot`
7. **Pass condition:** "No argument fallacies detected." is visible; no annotated block or cards shown.

   **Note:** If the model still detects arguments in this text (ML models vary), substitute with shorter purely-factual input or increase the confidence threshold in `backend/pipeline/classifier.py`.

---

## TC-11 — Re-analyze resets state

**Goal:** Running a second analysis after resolving cards resets all resolutions; previously resolved cards are gone.

**Setup:** Complete TC-02 and resolve at least one finding card (TC-03 or TC-04).

1. After resolving ≥1 card, `browser_snapshot` — confirm at least one `ResolvedCard` is visible
2. `browser_fill` textarea with new or the same sample text (overwrite is fine)
3. `browser_click` "Analyze →"
4. `browser_wait_for` text `"finding"` — timeout: 60 000 ms (new results loaded)
5. `browser_snapshot` — confirm:
   - Previously resolved cards are **gone** — no `ResolvedCard` badges from the prior run
   - All new finding cards show as unresolved `ConfirmedCard` or `PossiblyCard` with challenge buttons
   - Inline highlights are fully opaque (not dimmed)
6. **Pass condition:** No `ResolvedCard` from the previous run is visible; all new cards show unresolved state.

---

## TC-12 — Loading state while analysis is running

**Goal:** The UI shows a loading indicator and blocks re-submission while the backend is processing.

1. `browser_navigate` to `http://localhost:5173`
2. `browser_fill` textarea with the TC-02 sample text
3. `browser_click` "Analyze →"
4. `browser_wait_for` text `"Analyzing…"` — timeout: 3 000 ms (confirm loading state appeared before results arrive)
5. `browser_snapshot` — confirm:
   - Button text shows `"Analyzing…"`
   - Button is disabled (cannot be clicked again)
6. `browser_wait_for` text `"finding"` — timeout: 60 000 ms (wait for results)
7. `browser_snapshot` after results load:
   - Button text reverted to `"Analyze →"`
   - Button is enabled again
8. **Pass condition:** Button shows "Analyzing…" and is disabled during analysis; reverts after completion.

---

## TC-13 — CLEARED highlight dims in annotated text

**Goal:** After resolving any span as CLEARED, the corresponding inline highlight dims to indicate the text is no longer flagged.

**Setup:** Complete TC-02 and TC-04 (resolve one span as CLEARED).

1. After the CLEARED resolution, `browser_evaluate`:
   ```js
   const dimmed = [...document.querySelectorAll('mark')].filter(m => m.style.opacity === '0.4')
   dimmed.map(m => m.textContent)
   ```
   Expect an array containing the text of the CLEARED span.
2. `browser_take_screenshot` — visually confirm the highlighted text appears desaturated/dimmed compared to still-active highlights.
3. **Pass condition:** The CLEARED span's `<mark>` has `opacity: 0.4`; other unresolved `<mark>` elements remain at `opacity: 1`.

---

## TC-14 — Degraded content badge on fallback response

**Goal:** When the backend returns template content (no OpenAI key or API failure), the challenge shows a degraded warning.

**Setup:** This test requires the backend to be running with an invalid API key. Have a human operator restart the backend as: `OPENAI_API_KEY=invalid uvicorn main:app --reload --port 8000`. The Playwright agent cannot execute terminal commands — confirm the backend is running in fallback mode before starting steps.

1. `browser_navigate` to `http://localhost:5173`
2. `browser_fill` textarea with the TC-02 sample text
3. `browser_click` "Analyze →"
4. `browser_wait_for` text `"finding"` — timeout: 60 000 ms
5. `browser_snapshot` — look for the degraded badge in at least one challenge section:
   - Text: `"⚠ Detailed explanation unavailable — showing standard challenge"`
   - This badge appears in the `Challenge` component when `span.content_generated === false`
6. **Pass condition:** At least one finding card shows the degraded warning; cards are still interactive and resolvable.

   **Cleanup:** Have a human operator restore a valid `OPENAI_API_KEY` and restart the backend before running further tests.

---

## TC-A — Fallback challenge content is type-specific

**Goal:** When the backend is in fallback mode (no OpenAI key), each finding card shows challenge text specific to its detected fallacy type — not generic `non_sequitur` content for every finding.

**Note:** This directly exercises the `challenge_types._MAP` lookup. If all challenge sections show identical content regardless of fallacy type, the `_MAP` case-mismatch bug is present — every fallacy label maps to the default `non_sequitur` entry.

**Setup:** Same as TC-14 — backend running with `OPENAI_API_KEY=invalid`. Requires at least two finding cards with different `fallacy_type` values.

1. `browser_navigate` to `http://localhost:5173`
2. `browser_fill` textarea with the TC-02 sample text
3. `browser_click` "Analyze →"
4. `browser_wait_for` text `"finding"` — timeout: 60 000 ms
5. `browser_snapshot` — note the fallacy type shown in each card header (e.g. "Confirmed — Ad Hominem", "Confirmed — Slippery Slope")
6. `browser_evaluate`:
   ```js
   // Collect first 60 chars of each card's first <p> to compare challenge text
   [...document.querySelectorAll('[id^="card-"]')].map(card => ({
     header: card.querySelector('strong')?.textContent?.trim(),
     challengeSnippet: card.querySelector('p')?.textContent?.trim().slice(0, 80)
   }))
   ```
   Each entry's `challengeSnippet` should differ when the headers show different fallacy types. If every snippet is identical (especially if it references "non sequitur"), the `_MAP` lookup is failing.
7. `browser_take_screenshot`
8. **Pass condition:** Cards with different fallacy types show distinct challenge text. Identical challenge text across cards with different types is a failure.

   **Cleanup:** Restore a valid `OPENAI_API_KEY` before continuing.

---

## TC-B — Activate cascade does not overwrite resolved spans

**Goal:** When a cascade rule with `effect: "activate"` fires, it does NOT reset spans the user has already resolved. Previously-resolved cards must stay resolved.

**Note:** This tests the guard missing in `useFallacyCollection.ts` — `getCascades` currently maps `activate` rules to `'PENDING'` with no check on existing resolution state.

**Setup:** Complete TC-02. Requires at least one `activate` dependency rule in the response. If the response contains no `activate` rules, mark N/A.

1. `browser_snapshot` — confirm at least 2 unresolved cards are visible
2. Resolve one card using either YES or NO. Note the card ID and which resolution (CONFIRMED or CLEARED)
3. `browser_snapshot` — confirm that card shows a `ResolvedCard` badge (no challenge buttons)
4. Resolve a different card that could plausibly be a cascade source
5. `browser_snapshot` — confirm:
   - The card resolved in step 2 is **still in `ResolvedCard` state** — badge visible, no challenge buttons
   - It has NOT reverted to `ConfirmedCard` or `PossiblyCard`
6. `browser_evaluate`:
   ```js
   // Confirm the specific card is still resolved — no YES/NO buttons inside it
   const resolvedCards = [...document.querySelectorAll('[id^="card-"]')]
     .filter(c => !c.querySelector('button') || c.querySelector('button')?.textContent?.includes('Review anyway'))
   resolvedCards.length
   ```
   Should be ≥ 2 (at least both resolved cards remain resolved).
7. **Pass condition:** Previously-resolved cards remain resolved after any cascade fires. A card reverting to unresolved state is a failure.

---

## TC-C — LegitimacyComparison renders both columns

**Goal:** For a `PossiblyCard` where both `if_legitimate` and `if_fallacy` fields are present, the two-column comparison renders correctly with non-empty text in both columns.

**Setup:** Complete TC-02. Requires at least one `PossiblyCard` in results.

1. `browser_snapshot` — locate a card with "⚠ Possibly —" in its header
2. `browser_evaluate`:
   ```js
   const possiblyCards = [...document.querySelectorAll('[id^="card-"]')]
     .filter(c => c.textContent.includes('⚠ Possibly'))
   possiblyCards.map(c => ({
     hasLegitimate: c.textContent.includes('IF LEGITIMATE'),
     hasFallacy: c.textContent.includes('IF A FALLACY')
   }))
   ```
   Expect at least one entry with both `hasLegitimate: true` and `hasFallacy: true`.
3. `browser_snapshot` — visually confirm:
   - "✓ IF LEGITIMATE" column header is visible
   - "✗ IF A FALLACY" column header is visible
   - Both columns have non-empty body text below their headers
4. **Pass condition:** Both `LegitimacyComparison` columns are visible with non-empty text. If the section is absent despite both fields appearing in the response, the component is not rendering.

   **If no `PossiblyCard` appears:** The TC-02 sample text may not produce ambiguous findings this run. Try with: *"This data could support either interpretation. Some researchers have raised doubts."*

---

## Selector reference

| Element | How to locate |
|---------|--------------|
| Textarea | `aria-label="Text to analyze for argument fallacies"` |
| Analyze button | `button` containing text "Analyze →" or "Analyzing…" |
| Inline highlight | `mark[role="button"]` |
| ConfirmedCard | `[id^="card-"]` containing "Confirmed —" in a bold header |
| PossiblyCard | `[id^="card-"]` containing "⚠ Possibly —" |
| MootCard | `[id^="card-"]` containing "MOOT —" |
| ResolvedCard | `[id^="card-"]` containing "Cleared — not a fallacy" or a "Confirmed —" badge without challenge buttons |
| Challenge YES button | First `button` inside a challenge section (red, left button) |
| Challenge NO button | Second `button` inside a challenge section (green, right button) |
| "Review anyway →" | `button` containing "Review anyway →" |
| No-results message | `p` containing "No argument fallacies detected." |
| Error message | `p` containing "Analysis failed" |
| Metadata line | `p` containing "finding" |
| Degraded badge | element containing "⚠ Detailed explanation unavailable" |
