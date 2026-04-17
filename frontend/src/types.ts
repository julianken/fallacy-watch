export type ChallengeType =
  | 'counterexample' | 'domain_check' | 'meaning_check'
  | 'representation_check' | 'non_sequitur' | 'premise_check'

export interface Question { text: string; yes_label: string; no_label: string }
export interface Challenge { type: ChallengeType; question: Question }

export interface DependencyRule {
  source_id: string; dependent_id: string
  when: 'CONFIRMED' | 'CLEARED'; effect: 'moot' | 'activate'; reason: string
}

export interface SpanResult {
  id: string; text: string; start: number; end: number
  status: 'confirmed' | 'possibly'; fallacy_type: string; explanation: string
  challenge: Challenge; if_legitimate: string | null; if_fallacy: string | null
  content_generated: boolean
}

export interface AnalysisMeta {
  sentence_count: number; argument_span_count: number
  fallacy_count: number; processing_ms: number
}

export interface AnalyzeResponse { spans: SpanResult[]; rules: DependencyRule[]; meta: AnalysisMeta }

export type Resolution = 'PENDING' | 'CONFIRMED' | 'CLEARED' | 'MOOT' | 'DORMANT'
