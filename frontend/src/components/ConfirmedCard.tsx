import type { SpanResult, Resolution } from '../types'
import { Challenge } from './Challenge'
interface Props { span: SpanResult; onResolve: (id: string, o: Resolution) => void }
export function ConfirmedCard({ span, onResolve }: Props) {
  return (
    <div id={`card-${span.id}`} style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.35)', borderRadius: 8, padding: 14, marginBottom: 12 }}>
      <div style={{ fontWeight: 'bold', color: '#fca5a5', marginBottom: 4 }}>Confirmed — {span.fallacy_type}</div>
      <div style={{ color: '#fca5a5', opacity: 0.75, fontStyle: 'italic', marginBottom: 10 }}>"{span.text}"</div>
      <div style={{ opacity: 0.65, lineHeight: 1.55, marginBottom: 12 }}>{span.explanation}</div>
      <Challenge challenge={span.challenge} onResolve={o => onResolve(span.id, o)} degraded={!span.content_generated} />
    </div>
  )
}
