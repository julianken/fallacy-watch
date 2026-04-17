import type { AnalyzeResponse } from './types'

export async function analyze(text: string): Promise<AnalyzeResponse> {
  const resp = await fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!resp.ok) throw new Error(String(resp.status))
  return resp.json()
}
