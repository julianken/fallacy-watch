import { describe, expect, it } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFallacyCollection } from './useFallacyCollection'
import type { DependencyRule, Resolution, SpanResult } from '../types'

interface FixtureSpan { id: string; status: string }
interface FixtureRule {
  source_id: string
  dependent_id: string
  when: 'CONFIRMED' | 'CLEARED'
  effect: 'moot'
  reason: string
}
interface FixtureAction { resolve: string; outcome: Resolution }
interface CascadeFixture {
  name: string
  spans: FixtureSpan[]
  rules: FixtureRule[]
  actions: FixtureAction[]
  expected_final_state: Record<string, Resolution>
}

// Shared golden fixtures live OUTSIDE frontend/ so the Python collection can
// read the same files. Drift between the two implementations becomes a test-
// time error in whichever language regressed. We use Vite's import.meta.glob
// (resolved at build time) instead of Node fs so the test type-checks under
// the browser-only tsconfig (no @types/node, ESM, no __dirname).
const fixtureModules = import.meta.glob<CascadeFixture>(
  '../../../fixtures/cascade-contract/*.json',
  { eager: true, import: 'default' },
)

const fixtures: Array<{ path: string; fx: CascadeFixture }> = Object.entries(fixtureModules)
  .map(([p, fx]) => ({ path: p, fx }))
  .sort((a, b) => a.path.localeCompare(b.path))

function asSpanResults(spans: FixtureSpan[]): SpanResult[] {
  // The hook only consumes id and status from each span (init + statusOf
  // lookups). Pad with the rest of the SpanResult shape so we can keep the
  // contract fixtures minimal without weakening typing.
  return spans.map(s => ({
    id: s.id,
    text: '',
    start: 0,
    end: 0,
    status: s.status as SpanResult['status'],
    fallacy_type: '',
    explanation: '',
    challenge: { type: 'premise_check', question: { text: '', yes_label: '', no_label: '' } },
    if_legitimate: null,
    if_fallacy: null,
    content_generated: false,
  }))
}

function asDependencyRules(rules: FixtureRule[]): DependencyRule[] {
  return rules.map(r => ({ ...r }))
}

describe('cascade contract', () => {
  for (const { path, fx } of fixtures) {
    it(fx.name || path, () => {
      const { result } = renderHook(() =>
        useFallacyCollection(asSpanResults(fx.spans), asDependencyRules(fx.rules), 'run-1'),
      )
      act(() => {
        for (const action of fx.actions) {
          result.current.resolve(action.resolve, action.outcome)
        }
      })
      const actual = Object.fromEntries(
        fx.spans.map(s => [s.id, result.current.statusOf(s.id)]),
      )
      expect(actual).toEqual(fx.expected_final_state)
    })
  }
})
