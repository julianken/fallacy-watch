import { describe, expect, it } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import * as fs from 'node:fs'
import * as path from 'node:path'
import { useFallacyCollection } from './useFallacyCollection'
import type { DependencyRule, Resolution, SpanResult } from '../types'

// Shared golden fixtures live OUTSIDE frontend/ so the Python collection can
// read the same files. Drift between the two implementations becomes a test-
// time error in whichever language regressed.
const FIXTURES_DIR = path.resolve(__dirname, '../../../fixtures/cascade-contract')

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

const fixtures = fs
  .readdirSync(FIXTURES_DIR)
  .filter(f => f.endsWith('.json'))
  .sort()

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
  for (const file of fixtures) {
    const fx: CascadeFixture = JSON.parse(
      fs.readFileSync(path.join(FIXTURES_DIR, file), 'utf8'),
    )
    it(fx.name, () => {
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
