import type { Challenge as ChallengeType, Resolution } from '../types'
interface Props { challenge: ChallengeType; onResolve: (o: Resolution) => void; degraded?: boolean }
export function Challenge({ challenge, onResolve, degraded }: Props) {
  const { question } = challenge
  return (
    <div style={{ marginTop: 12 }}>
      {degraded && <p style={{ fontSize: '0.8em', opacity: 0.45, marginBottom: 8 }}>⚠ Detailed explanation unavailable — showing standard challenge</p>}
      <p style={{ fontWeight: 600, lineHeight: 1.5, marginBottom: 10 }}>{question.text}</p>
      <div style={{ display: 'flex', gap: 8 }}>
        <button onClick={() => onResolve('CONFIRMED')}
          style={{ flex: 1, padding: '7px 8px', borderRadius: 5, cursor: 'pointer', border: '1px solid rgba(239,68,68,0.5)', background: 'rgba(239,68,68,0.1)', color: '#fca5a5' }}>
          {question.yes_label}
        </button>
        <button onClick={() => onResolve('CLEARED')}
          style={{ flex: 1, padding: '7px 8px', borderRadius: 5, cursor: 'pointer', border: '1px solid rgba(74,222,128,0.5)', background: 'rgba(74,222,128,0.1)', color: '#86efac' }}>
          {question.no_label}
        </button>
      </div>
    </div>
  )
}
