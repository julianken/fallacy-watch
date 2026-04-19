import { useState, useCallback, useEffect, useMemo } from 'react'
import type { SpanResult, DependencyRule, Resolution } from '../types'

interface Cascade { id: string; resolution: Resolution; reason: string }

interface UseFallacyCollection {
  resolve: (id: string, outcome: Resolution) => Cascade[]
  previewCascade: (id: string, outcome: Resolution) => Cascade[]
  statusOf: (id: string) => Resolution
  isComplete: () => boolean
}

export function useFallacyCollection(
  spans: SpanResult[],
  rules: DependencyRule[],
  runId: string | number
): UseFallacyCollection {
  const [resolutions, setResolutions] = useState<Record<string, Resolution>>(() => {
    const init: Record<string, Resolution> = {}
    for (const span of spans) init[span.id] = 'PENDING'
    return init
  })

  useEffect(() => {
    setResolutions(Object.fromEntries(spans.map(s => [s.id, 'PENDING' as Resolution])))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId])

  const getCascades = useCallback(
    (id: string, outcome: Resolution): Cascade[] =>
      rules
        .filter(r => r.source_id === id && r.when === outcome)
        .map(r => ({
          id: r.dependent_id,
          resolution: r.effect === 'moot' ? 'MOOT' : ('PENDING' as Resolution),
          reason: r.reason,
        })),
    [rules]
  )

  const resolve = useCallback(
    (id: string, outcome: Resolution): Cascade[] => {
      const cascades = getCascades(id, outcome)
      setResolutions(prev => {
        const next = { ...prev, [id]: outcome }
        for (const c of cascades) {
          // activate must not overwrite a user decision; moot correctly overrides
          if (c.resolution === 'PENDING' && (prev[c.id] === 'CONFIRMED' || prev[c.id] === 'CLEARED')) continue
          next[c.id] = c.resolution
        }
        return next
      })
      return cascades
    },
    [getCascades]
  )

  const previewCascade = useCallback(
    (id: string, outcome: Resolution): Cascade[] => getCascades(id, outcome),
    [getCascades]
  )

  const statusOf = useCallback(
    (id: string): Resolution => resolutions[id] ?? 'PENDING',
    [resolutions]
  )

  const isComplete = useCallback(
    () => Object.values(resolutions).every(r => r !== 'PENDING'),
    [resolutions]
  )

  return useMemo(
    () => ({ resolve, previewCascade, statusOf, isComplete }),
    [resolve, previewCascade, statusOf, isComplete]
  )
}
