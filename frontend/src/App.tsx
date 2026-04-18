import { useState } from 'react'
import type { AnalyzeResponse } from './types'
import { analyze } from './api'
import { TextInput } from './components/TextInput'
import { AnnotatedText } from './components/AnnotatedText'
import { FindingsList } from './components/FindingsList'
import { useFallacyCollection } from './hooks/useFallacyCollection'

export default function App() {
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [runId, setRunId] = useState(0)
  const { statusOf, resolve } = useFallacyCollection(result?.spans ?? [], result?.rules ?? [], runId)

  async function handleAnalyze(text: string) {
    setLoading(true); setError(null); setInputText(text)
    try {
      setResult(await analyze(text))
      setRunId(prev => prev + 1)
    }
    catch { setError('Analysis failed. Check your connection and try again.') }
    finally { setLoading(false) }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '32px 16px', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', background: '#0f1117', minHeight: '100vh', color: '#e2e8f0' }}>
      <h1 style={{ fontSize: '1.6em', fontWeight: 700, marginBottom: 4 }}>fallacy-watch</h1>
      <p style={{ opacity: 0.5, marginBottom: 24 }}>Analyze any text for argument fallacies.</p>
      <TextInput onAnalyze={handleAnalyze} loading={loading} />
      {error && <p data-testid="error-message" style={{ color: '#fca5a5', marginBottom: 16 }}>{error}</p>}
      {result && !loading && (
        result.spans.length === 0
          ? <p data-testid="no-fallacies-message" style={{ opacity: 0.5 }}>No argument fallacies detected.</p>
          : <>
              <div data-testid="annotated-text" style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 8, padding: 16, marginBottom: 24, lineHeight: 1.8 }}>
                <AnnotatedText text={inputText} spans={result.spans} statusOf={statusOf}
                  onSpanClick={id => document.getElementById(`card-${id}`)?.scrollIntoView({ behavior: 'smooth' })} />
              </div>
              <p data-testid="meta-line" style={{ opacity: 0.4, fontSize: '0.8em', marginBottom: 16 }}>
                {result.meta.fallacy_count} finding{result.meta.fallacy_count !== 1 ? 's' : ''} · {result.meta.processing_ms}ms
              </p>
              <FindingsList spans={result.spans} rules={result.rules} resolve={resolve} statusOf={statusOf} />
            </>
      )}
    </div>
  )
}
