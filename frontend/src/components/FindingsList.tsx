import { useState } from 'react'
import type { SpanResult, DependencyRule, Resolution } from '../types'
import { useFallacyCollection } from '../hooks/useFallacyCollection'
import { ConfirmedCard } from './ConfirmedCard'
import { PossiblyCard } from './PossiblyCard'
import { MootCard } from './MootCard'
interface Props { spans: SpanResult[]; rules: DependencyRule[]; onStatusChange: (id: string, r: Resolution) => void }
export function FindingsList({ spans, rules, onStatusChange }: Props) {
  const { resolve, statusOf } = useFallacyCollection(spans, rules)
  const [reviewed, setReviewed] = useState<Set<string>>(new Set())
  function handleResolve(id: string, outcome: Resolution) {
    resolve(id, outcome)
    onStatusChange(id, outcome)
  }
  return (
    <div>
      {[...spans].sort((a, b) => a.start - b.start).map(span => {
        const status = statusOf(span.id)
        if (status === 'MOOT' && !reviewed.has(span.id)) {
          const rule = rules.find(r => r.dependent_id === span.id && r.effect === 'moot')
          return <MootCard key={span.id} span={span} reason={rule?.reason ?? 'resolved by cascade'} onReviewAnyway={id => setReviewed(prev => new Set(prev).add(id))} />
        }
        return span.status === 'confirmed'
          ? <ConfirmedCard key={span.id} span={span} onResolve={handleResolve} />
          : <PossiblyCard key={span.id} span={span} onResolve={handleResolve} />
      })}
    </div>
  )
}
