import type { SpanResult, Resolution } from '../types'
import { formatFallacyType } from '../utils/fallacyColors'
interface Props { span: SpanResult; outcome: Resolution }
export function ResolvedCard({ span, outcome }: Props) {
  const isConfirmed = outcome === 'CONFIRMED'
  return (
    <div id={`card-${span.id}`} data-testid={`card-resolved-${span.id}`} style={{
      background: isConfirmed ? 'rgba(239,68,68,0.08)' : 'rgba(74,222,128,0.06)',
      border: `1px solid ${isConfirmed ? 'rgba(239,68,68,0.3)' : 'rgba(74,222,128,0.25)'}`,
      borderRadius: 8, padding: 14, marginBottom: 12, opacity: 0.75,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span style={{
          display: 'inline-block', padding: '2px 8px', borderRadius: 4, fontSize: '0.85em',
          background: isConfirmed ? 'rgba(239,68,68,0.2)' : 'rgba(74,222,128,0.15)',
          color: isConfirmed ? '#fca5a5' : '#86efac',
          border: `1px solid ${isConfirmed ? 'rgba(239,68,68,0.3)' : 'rgba(74,222,128,0.3)'}`,
        }}>
          {isConfirmed ? `Confirmed — ${formatFallacyType(span.fallacy_type)}` : 'Cleared — not a fallacy'}
        </span>
      </div>
      <div style={{ color: 'inherit', opacity: 0.5, fontStyle: 'italic', fontSize: '0.9em' }}>"{span.text}"</div>
    </div>
  )
}
