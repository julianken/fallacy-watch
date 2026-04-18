import { useState } from 'react'
import type { SpanResult, DependencyRule, Resolution } from '../types'
import { ConfirmedCard } from './ConfirmedCard'
import { PossiblyCard } from './PossiblyCard'
import { MootCard } from './MootCard'
import { ResolvedCard } from './ResolvedCard'
interface Props {
  spans: SpanResult[]
  rules: DependencyRule[]
  resolve: (id: string, outcome: Resolution) => void
  statusOf: (id: string) => Resolution
}
export function FindingsList({ spans, rules, resolve, statusOf }: Props) {
  const [reviewed, setReviewed] = useState<Set<string>>(new Set())
  return (
    <div data-testid="findings-list">
      {[...spans].sort((a, b) => a.start - b.start).map(span => {
        const status = statusOf(span.id)
        if (status === 'MOOT' && !reviewed.has(span.id)) {
          const rule = rules.find(r => r.dependent_id === span.id && r.effect === 'moot')
          return <MootCard key={span.id} span={span} reason={rule?.reason ?? 'resolved by cascade'} onReviewAnyway={id => setReviewed(prev => new Set(prev).add(id))} />
        }
        if (status === 'CONFIRMED' || status === 'CLEARED') {
          return <ResolvedCard key={span.id} span={span} outcome={status} />
        }
        return span.status === 'confirmed'
          ? <ConfirmedCard key={span.id} span={span} onResolve={resolve} />
          : <PossiblyCard key={span.id} span={span} onResolve={resolve} />
      })}
    </div>
  )
}
