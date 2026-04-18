import type { SpanResult, Resolution } from '../types'
import { Challenge } from './Challenge'
import { LegitimacyComparison } from './LegitimacyComparison'
import { formatFallacyType } from '../utils/fallacyColors'
interface Props { span: SpanResult; onResolve: (id: string, o: Resolution) => void }
export function PossiblyCard({ span, onResolve }: Props) {
  return (
    <div id={`card-${span.id}`} style={{ background: 'rgba(251,191,36,0.08)', border: '2px dashed rgba(251,191,36,0.45)', borderRadius: 8, padding: 14, marginBottom: 12 }}>
      <div style={{ fontWeight: 'bold', color: '#fde68a', marginBottom: 4 }}>⚠ Possibly — {formatFallacyType(span.fallacy_type)}</div>
      <div style={{ color: '#fde68a', opacity: 0.75, fontStyle: 'italic', marginBottom: 10 }}>"{span.text}"</div>
      <div style={{ opacity: 0.65, lineHeight: 1.55, marginBottom: 4 }}>{span.explanation}</div>
      {span.if_legitimate && span.if_fallacy && (
        <LegitimacyComparison ifLegitimate={span.if_legitimate} ifFallacy={span.if_fallacy} />
      )}
      <Challenge challenge={span.challenge} onResolve={o => onResolve(span.id, o)} degraded={!span.content_generated} />
    </div>
  )
}
