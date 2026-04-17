import { renderHook, act } from '@testing-library/react'
import { useFallacyCollection } from '../hooks/useFallacyCollection'
import type { SpanResult, DependencyRule } from '../types'

const makeSpan = (id: string): SpanResult => ({
  id, text: 'test', start: 0, end: 4, status: 'possibly',
  fallacy_type: 'Ad Populum', explanation: '', content_generated: true,
  challenge: { type: 'premise_check', question: { text: 'q', yes_label: 'y', no_label: 'n' } },
  if_legitimate: null, if_fallacy: null,
})

const rule: DependencyRule = {
  source_id: 'a', dependent_id: 'b', when: 'CONFIRMED', effect: 'moot', reason: 'premise failed',
}

it('resolve CONFIRMED cascades MOOT to dependent', () => {
  const { result } = renderHook(() => useFallacyCollection([makeSpan('a'), makeSpan('b')], [rule]))
  act(() => { result.current.resolve('a', 'CONFIRMED') })
  expect(result.current.statusOf('b')).toBe('MOOT')
})

it('resolve CLEARED activates DORMANT dependent', () => {
  const activateRule: DependencyRule = { ...rule, when: 'CLEARED', effect: 'activate' }
  const { result } = renderHook(() => useFallacyCollection([makeSpan('a'), makeSpan('b')], [activateRule]))
  act(() => { result.current.resolve('a', 'CLEARED') })
  expect(result.current.statusOf('b')).toBe('PENDING')
})

it('isComplete false when spans pending', () => {
  const { result } = renderHook(() => useFallacyCollection([makeSpan('a')], []))
  expect(result.current.isComplete()).toBe(false)
})

it('isComplete true when all resolved', () => {
  const { result } = renderHook(() => useFallacyCollection([makeSpan('a')], []))
  act(() => { result.current.resolve('a', 'CONFIRMED') })
  expect(result.current.isComplete()).toBe(true)
})

it('previewCascade does not mutate state', () => {
  const { result } = renderHook(() => useFallacyCollection([makeSpan('a'), makeSpan('b')], [rule]))
  act(() => { result.current.previewCascade('a', 'CONFIRMED') })
  expect(result.current.statusOf('b')).toBe('PENDING')
})
