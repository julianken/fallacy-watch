import { useState } from 'react'
interface Props { onAnalyze: (text: string) => void; loading: boolean }
export function TextInput({ onAnalyze, loading }: Props) {
  const [text, setText] = useState('')
  return (
    <div style={{ marginBottom: 24 }}>
      <textarea value={text} onChange={e => setText(e.target.value)} rows={8}
        placeholder="Paste any text to analyze for argument fallacies..."
        style={{ width: '100%', padding: 12, borderRadius: 8, fontSize: '0.95em', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.15)', color: 'inherit', resize: 'vertical', boxSizing: 'border-box' }} />
      <div style={{ textAlign: 'right', marginTop: 8 }}>
        <button onClick={() => text.trim() && onAnalyze(text)} disabled={loading || !text.trim()}
          style={{ padding: '8px 20px', borderRadius: 6, border: 'none', cursor: 'pointer', background: loading ? 'rgba(99,102,241,0.4)' : '#6366f1', color: 'white', fontSize: '0.95em' }}>
          {loading ? 'Analyzing…' : 'Analyze →'}
        </button>
      </div>
    </div>
  )
}
