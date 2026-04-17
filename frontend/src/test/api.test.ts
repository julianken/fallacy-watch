import { it, expect, vi, beforeEach } from 'vitest'
import { analyze } from '../api'

beforeEach(() => { vi.restoreAllMocks() })

it('returns data on success', async () => {
  const mockData = { spans: [], rules: [], meta: { sentence_count: 1, argument_span_count: 0, fallacy_count: 0, processing_ms: 10 } }
  vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
    new Response(JSON.stringify(mockData), { status: 200 })
  )
  const result = await analyze('some text')
  expect(result.spans).toEqual([])
})

it('throws on non-200', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
    new Response('{"detail":"error"}', { status: 422 })
  )
  await expect(analyze('bad')).rejects.toThrow('422')
})
