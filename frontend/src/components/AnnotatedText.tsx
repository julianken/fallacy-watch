import type { SpanResult, Resolution } from '../types'
import { splitBySpans } from '../utils/splitBySpans'
import { Highlight } from './Highlight'
interface Props { text: string; spans: SpanResult[]; statusOf: (id: string) => Resolution; onSpanClick: (id: string) => void }
export function AnnotatedText({ text, spans, statusOf, onSpanClick }: Props) {
  return (
    <p style={{ lineHeight: 2, fontSize: '0.95em' }}>
      {splitBySpans(text, spans).map((seg, i) =>
        seg.type === 'plain'
          ? <span key={i}>{seg.text}</span>
          : <Highlight key={i} span={seg.span} text={seg.text} resolution={statusOf(seg.span.id)} onClick={() => onSpanClick(seg.span.id)} />
      )}
    </p>
  )
}
