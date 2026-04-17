import type { SpanResult } from '../types'

export type Segment =
  | { type: 'plain'; text: string }
  | { type: 'span'; text: string; span: SpanResult }

export function splitBySpans(text: string, spans: SpanResult[]): Segment[] {
  const sorted = [...spans].sort((a, b) => a.start - b.start)
  const segments: Segment[] = []
  let cursor = 0
  for (const span of sorted) {
    if (span.start > cursor) segments.push({ type: 'plain', text: text.slice(cursor, span.start) })
    segments.push({ type: 'span', text: text.slice(span.start, span.end), span })
    cursor = span.end
  }
  if (cursor < text.length) segments.push({ type: 'plain', text: text.slice(cursor) })
  return segments
}
