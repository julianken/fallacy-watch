import type { SpanResult, Resolution } from '../types'
import { fallacyBg, fallacyBorder } from '../utils/fallacyColors'
interface Props { span: SpanResult; text: string; resolution: Resolution; onClick: () => void }
export function Highlight({ span, text, resolution, onClick }: Props) {
  const isMoot = resolution === 'MOOT' || resolution === 'CLEARED'
  return (
    <mark onClick={onClick} role="button" tabIndex={0} onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && onClick()} style={{
      background: isMoot ? 'rgba(255,255,255,0.05)' : fallacyBg(span.fallacy_type),
      borderBottom: `2px ${span.status === 'possibly' ? 'dashed' : 'solid'} ${isMoot ? 'rgba(255,255,255,0.2)' : fallacyBorder(span.fallacy_type)}`,
      borderRadius: 3, padding: '1px 3px', cursor: 'pointer', color: 'inherit', opacity: isMoot ? 0.4 : 1,
    }}>
      {text}
    </mark>
  )
}
