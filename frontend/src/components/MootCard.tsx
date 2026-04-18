import type { SpanResult } from '../types'
import { formatFallacyType } from '../utils/fallacyColors'
interface Props { span: SpanResult; reason: string; onReviewAnyway: (id: string) => void }
export function MootCard({ span, reason, onReviewAnyway }: Props) {
  return (
    <div id={`card-${span.id}`} data-testid={`card-moot-${span.id}`} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, padding: 12, marginBottom: 12, opacity: 0.5 }}>
      <div style={{ fontSize: '0.8em', marginBottom: 6 }}>MOOT — {formatFallacyType(span.fallacy_type)}</div>
      <div style={{ fontStyle: 'italic', marginBottom: 4 }}>"{span.text}"</div>
      <div style={{ fontSize: '0.85em', marginBottom: 10, opacity: 0.7 }}>{reason}</div>
      <button onClick={() => onReviewAnyway(span.id)} style={{ padding: '4px 10px', borderRadius: 4, border: '1px solid rgba(255,255,255,0.15)', background: 'transparent', color: 'inherit', cursor: 'pointer', fontSize: '0.85em' }}>
        Review anyway →
      </button>
    </div>
  )
}
