export function formatFallacyType(t: string): string {
  return t.replace(/\b\w/g, c => c.toUpperCase())
}

const BG: Record<string, string> = {
  'Ad Hominem':             'rgba(248,113,113,0.25)',
  'Ad Populum':             'rgba(239,68,68,0.25)',
  'Appeal To Emotion':      'rgba(244,114,182,0.25)',
  'Circular Reasoning':     'rgba(129,140,248,0.25)',
  'Equivocation':           'rgba(99,102,241,0.25)',
  'Fallacy Of Credibility': 'rgba(249,115,22,0.25)',
  'Fallacy Of Extension':   'rgba(52,211,153,0.25)',
  'Fallacy Of Logic':       'rgba(167,139,250,0.25)',
  'Fallacy Of Relevance':   'rgba(45,212,191,0.25)',
  'False Causality':        'rgba(251,146,60,0.25)',
  'False Dilemma':          'rgba(250,204,21,0.25)',
  'Faulty Generalization':  'rgba(251,191,36,0.25)',
  'Intentional':            'rgba(148,163,184,0.25)',
}
const BORDER: Record<string, string> = {
  'Ad Hominem':             '#f87171',
  'Ad Populum':             '#ef4444',
  'Appeal To Emotion':      '#f472b6',
  'Circular Reasoning':     '#818cf8',
  'Equivocation':           '#6366f1',
  'Fallacy Of Credibility': '#f97316',
  'Fallacy Of Extension':   '#34d399',
  'Fallacy Of Logic':       '#a78bfa',
  'Fallacy Of Relevance':   '#2dd4bf',
  'False Causality':        '#fb923c',
  'False Dilemma':          '#facc15',
  'Faulty Generalization':  '#fbbf24',
  'Intentional':            '#94a3b8',
}
export const fallacyBg = (t: string) => BG[formatFallacyType(t)] ?? 'rgba(148,163,184,0.2)'
export const fallacyBorder = (t: string) => BORDER[formatFallacyType(t)] ?? '#94a3b8'
