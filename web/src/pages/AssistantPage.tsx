import { useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../components/AppShell'
import { ApiError, api } from '../lib/api'
import { useAuth } from '../lib/auth'

type AskResult = {
  answer: string
  facts_used: string[]
  mode: string
  topics: string[]
}

const SUGGESTIONS: Record<string, string[]> = {
  admin: [
    'What is the programme pass rate?',
    'How many students are in each semester?',
    'Summarise campus attendance and assignments.',
  ],
  faculty: [
    'How is attendance looking in my courses?',
    'Which assignments still need submissions?',
    'Give me an overview of my teaching load.',
  ],
  student: [
    'What is my overall attendance?',
    'How did I do in my latest exams?',
    'What assignments do I still need to submit?',
  ],
}

export function AssistantPage() {
  const { token, logout, role } = useAuth()
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState<AskResult | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const suggestions = SUGGESTIONS[role || 'student'] || SUGGESTIONS.student

  async function ask(text: string) {
    if (!token || !text.trim()) return
    setLoading(true)
    setError('')
    try {
      const data = await api.post<AskResult>('/api/ai/ask', token, { question: text.trim() })
      setResult(data)
      setQuestion(text.trim())
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        logout()
        window.location.assign('/login')
        return
      }
      setError(err instanceof Error ? err.message : 'Assistant request failed')
    } finally {
      setLoading(false)
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    void ask(question)
  }

  return (
    <AppShell
      title="Academic assistant"
      subtitle="Answers only from your ERP records — attendance, marks, assignments, and notices."
    >
      {error ? <div className="toast error">{error}</div> : null}

      <form className="panel stack" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="q">Ask a question</label>
          <textarea
            id="q"
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. What is my attendance this semester?"
            required
          />
        </div>
        <div className="row-actions">
          {suggestions.map((prompt) => (
            <button
              key={prompt}
              className="btn btn-ghost btn-tiny"
              type="button"
              onClick={() => void ask(prompt)}
              disabled={loading}
            >
              {prompt}
            </button>
          ))}
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Looking up records…' : 'Ask'}
        </button>
      </form>

      {result ? (
        <section className="panel stack" style={{ marginTop: 18 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
            <h3 style={{ margin: 0 }}>Answer</h3>
            <span className="badge ok">{result.mode}</span>
          </div>
          <p style={{ whiteSpace: 'pre-wrap', margin: 0, lineHeight: 1.55 }}>{result.answer}</p>
          <div>
            <h4 style={{ margin: '0 0 8px' }}>Facts used</h4>
            <ul className="fact-list">
              {result.facts_used.map((fact) => (
                <li key={fact}>{fact}</li>
              ))}
            </ul>
          </div>
        </section>
      ) : null}
    </AppShell>
  )
}
