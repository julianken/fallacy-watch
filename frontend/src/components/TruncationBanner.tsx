import type { AnalysisMeta } from '../types'

interface Props { meta: AnalysisMeta }

export function TruncationBanner({ meta }: Props) {
  if (!meta.truncated) return null
  const original = meta.original_char_count ?? 0
  return (
    <div
      data-testid="truncation-banner"
      role="alert"
      style={{
        background: 'rgba(252, 211, 77, 0.12)',
        border: '1px solid rgba(252, 211, 77, 0.4)',
        color: '#fcd34d',
        borderRadius: 6,
        padding: '8px 12px',
        marginBottom: 16,
        fontSize: '0.85em',
      }}
    >
      Input was truncated. Only the first portion of your {original.toLocaleString()}-character text was analyzed.
    </div>
  )
}
