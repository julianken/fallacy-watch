export function formatFallacyType(t: string): string {
  return t.replace(/\b\w/g, c => c.toUpperCase())
}

const BG: Record<string, string> = {
  'Ad Populum':            'rgba(239,68,68,0.25)',
  'Fallacy of Logic':      'rgba(167,139,250,0.25)',
  'Faulty Generalization': 'rgba(251,191,36,0.25)',
  'Fallacy of Extension':  'rgba(52,211,153,0.25)',
  'Equivocation':          'rgba(99,102,241,0.25)',
  'Fallacy of Credibility':'rgba(249,115,22,0.25)',
}
const BORDER: Record<string, string> = {
  'Ad Populum':            '#ef4444',
  'Fallacy of Logic':      '#a78bfa',
  'Faulty Generalization': '#fbbf24',
  'Fallacy of Extension':  '#34d399',
  'Equivocation':          '#6366f1',
  'Fallacy of Credibility':'#f97316',
}
export const fallacyBg = (t: string) => BG[formatFallacyType(t)] ?? 'rgba(148,163,184,0.2)'
export const fallacyBorder = (t: string) => BORDER[formatFallacyType(t)] ?? '#94a3b8'
