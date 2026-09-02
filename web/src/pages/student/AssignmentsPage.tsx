import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../../components/AppShell'
import { ApiError, api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type AssignmentRow = {
  assignment_id: string
  sub_code: string
  sub_name: string
  title: string
  due_at: string
  max_score: number
  status: string
  score: number | null
}

type AssignmentDetail = {
  assignment_id: string
  sub_code: string
  title: string
  description: string | null
  due_at: string
  max_score: number
  my_submission: {
    content: string
    score: number | null
    feedback: string | null
    submitted_at: string
  } | null
}

export function StudentAssignmentsPage() {
  const { token, logout } = useAuth()
  const [rows, setRows] = useState<AssignmentRow[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [detail, setDetail] = useState<AssignmentDetail | null>(null)
  const [content, setContent] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)

  function handleAuth(err: unknown) {
    if (err instanceof ApiError && err.status === 401) {
      logout()
      window.location.assign('/login')
      return true
    }
    return false
  }

  function reloadList(currentToken: string) {
    return api.get<AssignmentRow[]>('/api/student/assignments', currentToken).then(setRows)
  }

  useEffect(() => {
    if (!token) return
    reloadList(token).catch((err) => {
      if (handleAuth(err)) return
      setError(err instanceof Error ? err.message : 'Failed to load assignments')
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  useEffect(() => {
    if (!token || !selectedId) {
      setDetail(null)
      return
    }
    api
      .get<AssignmentDetail>(`/api/student/assignments/${selectedId}`, token)
      .then((data) => {
        setDetail(data)
        setContent(data.my_submission?.content || '')
      })
      .catch((err) => {
        if (handleAuth(err)) return
        setError(err instanceof Error ? err.message : 'Failed to open assignment')
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, selectedId])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!token || !selectedId) return
    setSaving(true)
    setError('')
    setMessage('')
    try {
      await api.post(`/api/student/assignments/${selectedId}/submit`, token, {
        content: content.trim(),
      })
      setMessage('Submission saved.')
      await reloadList(token)
      const refreshed = await api.get<AssignmentDetail>(
        `/api/student/assignments/${selectedId}`,
        token,
      )
      setDetail(refreshed)
    } catch (err) {
      if (handleAuth(err)) return
      setError(err instanceof Error ? err.message : 'Submit failed')
    } finally {
      setSaving(false)
    }
  }

  const graded = detail?.my_submission?.score != null

  return (
    <AppShell title="Assignments" subtitle="Coursework for your semester — submit text responses here.">
      {error ? <div className="toast error">{error}</div> : null}
      {message ? <div className="toast success">{message}</div> : null}

      <section className="panel">
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Course</th>
                <th>Title</th>
                <th>Due</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.assignment_id}>
                  <td>{row.sub_code}</td>
                  <td>{row.title}</td>
                  <td>{new Date(row.due_at).toLocaleString()}</td>
                  <td>
                    {row.status}
                    {row.score != null ? ` · ${row.score}/${row.max_score}` : ''}
                  </td>
                  <td>
                    <button
                      className="btn btn-ghost btn-tiny"
                      type="button"
                      onClick={() => setSelectedId(row.assignment_id)}
                    >
                      Open
                    </button>
                  </td>
                </tr>
              ))}
              {!rows.length ? (
                <tr>
                  <td colSpan={5} className="empty">
                    No assignments posted for your semester yet.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      {detail ? (
        <form className="panel stack" style={{ marginTop: 18 }} onSubmit={onSubmit}>
          <div>
            <h3 style={{ margin: '0 0 6px' }}>
              {detail.sub_code} · {detail.title}
            </h3>
            <div style={{ color: 'var(--muted)' }}>
              Due {new Date(detail.due_at).toLocaleString()} · Max {detail.max_score}
            </div>
            {detail.description ? <p style={{ marginBottom: 0 }}>{detail.description}</p> : null}
          </div>
          {detail.my_submission?.feedback ? (
            <div className="toast success">Feedback: {detail.my_submission.feedback}</div>
          ) : null}
          <div className="field">
            <label htmlFor="work">Your submission</label>
            <textarea
              id="work"
              rows={8}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              disabled={graded}
              required
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={saving || graded}>
            {graded
              ? `Graded · ${detail.my_submission?.score}/${detail.max_score}`
              : saving
                ? 'Saving…'
                : detail.my_submission
                  ? 'Update submission'
                  : 'Submit work'}
          </button>
        </form>
      ) : null}
    </AppShell>
  )
}
