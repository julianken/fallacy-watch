interface Props { ifLegitimate: string; ifFallacy: string }
export function LegitimacyComparison({ ifLegitimate, ifFallacy }: Props) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, margin: '12px 0' }}>
      <div style={{ background: 'rgba(74,222,128,0.07)', border: '1px solid rgba(74,222,128,0.2)', borderRadius: 6, padding: 10, lineHeight: 1.55 }}>
        <span style={{ fontSize: '0.8em', color: '#86efac', opacity: 0.8, display: 'block', marginBottom: 5 }}>✓ IF LEGITIMATE</span>
        <span style={{ opacity: 0.75 }}>{ifLegitimate}</span>
      </div>
      <div style={{ background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 6, padding: 10, lineHeight: 1.55 }}>
        <span style={{ fontSize: '0.8em', color: '#fca5a5', opacity: 0.8, display: 'block', marginBottom: 5 }}>✗ IF A FALLACY</span>
        <span style={{ opacity: 0.75 }}>{ifFallacy}</span>
      </div>
    </div>
  )
}
