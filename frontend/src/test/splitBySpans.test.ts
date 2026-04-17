import { splitBySpans } from '../utils/splitBySpans'
import type { SpanResult } from '../types'

const makeSpan = (id: string, start: number, end: number): SpanResult => ({
  id, text: 'x', start, end, status: 'confirmed', fallacy_type: 'Ad Populum',
  explanation: '', content_generated: true,
  challenge: { type: 'premise_check', question: { text: '', yes_label: '', no_label: '' } },
  if_legitimate: null, if_fallacy: null,
})

it('splits into plain and span segments', () => {
  const segs = splitBySpans('Hello world, goodbye world.', [makeSpan('a', 6, 11)])
  expect(segs).toHaveLength(3)
  expect(segs[0]).toEqual({ type: 'plain', text: 'Hello ' })
  expect(segs[1].type).toBe('span')
  expect(segs[2]).toEqual({ type: 'plain', text: ', goodbye world.' })
})

it('handles span at start', () => {
  const segs = splitBySpans('Bad claim here.', [makeSpan('a', 0, 9)])
  expect(segs[0].type).toBe('span')
})

it('handles no spans', () => {
  const segs = splitBySpans('plain text', [])
  expect(segs).toHaveLength(1)
  expect(segs[0]).toEqual({ type: 'plain', text: 'plain text' })
})

it('handles adjacent spans', () => {
  const segs = splitBySpans('AABB', [makeSpan('a', 0, 2), makeSpan('b', 2, 4)])
  expect(segs.every(s => s.type === 'span')).toBe(true)
})
