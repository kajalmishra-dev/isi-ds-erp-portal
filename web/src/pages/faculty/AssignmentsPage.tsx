import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../../components/AppShell'
import { ApiError, api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type Offering = {
  offering_id: string
  sub_code: string
  sub_name: string
}

type Assignment = {
  assignment_id: string
  offering_id: string
  sub_code: string
  sub_name: string
  title: string
  description: string | null
  due_at: string
  max_score: number
  submission_count: number
  roster_count: number
}

type Submission = {
  submission_id: string
  enroll_no: string
  student_name: string
  content: string
  submitted_at: string
  score: number | null
  feedback: string | null
}

function dueInputValue(daysAhead = 14) {
  const d = new Date()
  d.setDate(d.getDate() + daysAhead)
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

export function FacultyAssignmentsPage() {
  const { token, logout } = useAuth()
  const [offerings, setOfferings] = useState<Offering[]>([])
  const [offeringId, setOfferingId] = useState('')
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [dueAt, setDueAt] = useState(dueInputValue)
  const [maxScore, setMaxScore] = useState(20)
  const [gradeDraft, setGradeDraft] = useState<Record<string, { score: string; feedback: string }>>({})
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

  function reloadAssignments(currentToken: string, oid?: string) {
    const qs = oid ? `?offering_id=${oid}` : ''
    return api.get<Assignment[]>(`/api/faculty/assignments${qs}`, currentToken).then(setAssignments)
  }

  useEffect(() => {
    if (!token) return
    api
      .get<Offering[]>('/api/faculty/offerings', token)
      .then((list) => {
        setOfferings(list)
        if (list[0]) setOfferingId(list[0].offering_id)
      })
      .catch((err) => {
        if (handleAuth(err)) return
        setError(err instanceof Error ? err.message : 'Failed to load offerings')
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  useEffect(() => {
    if (!token) return
    reloadAssignments(token, offeringId || undefined).catch((err) => {
      if (handleAuth(err)) return
      setError(err instanceof Error ? err.message : 'Failed to load assignments')
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, offeringId])

  useEffect(() => {
    if (!token || !selectedId) {
      setSubmissions([])
      return
    }
    api
      .get<Submission[]>(`/api/faculty/assignments/${selectedId}/submissions`, token)
      .then((rows) => {
        setSubmissions(rows)
        const draft: Record<string, { score: string; feedback: string }> = {}
        for (const row of rows) {
          draft[row.submission_id] = {
            score: row.score != null ? String(row.score) : '',
            feedback: row.feedback || '',
          }
        }
        setGradeDraft(draft)
      })
      .catch((err) => {
        if (handleAuth(err)) return
        setError(err instanceof Error ? err.message : 'Failed to load submissions')
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, selectedId])

  async function onCreate(event: FormEvent) {
    event.preventDefault()
    if (!token || !offeringId) return
    setSaving(true)
    setError('')
    setMessage('')
    try {
      await api.post(`/api/faculty/offerings/${offeringId}/assignments`, token, {
        title: title.trim(),
        description: description.trim() || null,
        due_at: new Date(dueAt).toISOString(),
        max_score: Number(maxScore),
      })
      setTitle('')
      setDescription('')
      setMessage('Assignment published.')
      await reloadAssignments(token, offeringId)
    } catch (err) {
      if (handleAuth(err)) return
      setError(err instanceof Error ? err.message : 'Could not create assignment')
    } finally {
      setSaving(false)
    }
  }

  async function gradeOne(submissionId: string) {
    if (!token || !selectedId) return
    const draft = gradeDraft[submissionId]
    if (!draft?.score) {
      setError('Enter a score before grading.')
      return
    }
    setError('')
    setMessage('')
    try {
      const updated = await api.patch<Submission>(
        `/api/faculty/assignments/${selectedId}/submissions/${submissionId}`,
        token,
        {
          score: Number(draft.score),
          feedback: draft.feedback.trim() || null,
        },
      )
      setSubmissions((prev) => prev.map((s) => (s.submission_id === submissionId ? updated : s)))
      setMessage(`Graded ${updated.student_name}.`)
      await reloadAssignments(token, offeringId)
    } catch (err) {
      if (handleAuth(err)) return
      setError(err instanceof Error ? err.message : 'Grading failed')
    }
  }

  return (
    <AppShell title="Assignments" subtitle="Publish coursework and grade student submissions.">
      {error ? <div className="toast error">{error}</div> : null}
      {message ? <div className="toast success">{message}</div> : null}

      <form className="panel stack" onSubmit={onCreate}>
        <h3 style={{ margin: 0 }}>New assignment</h3>
        <div className="grid-2">
          <div className="field">
            <label htmlFor="offering">Course</label>
            <select id="offering" value={offeringId} onChange={(e) => setOfferingId(e.target.value)}>
              {offerings.map((o) => (
                <option key={o.offering_id} value={o.offering_id}>
                  {o.sub_code} · {o.sub_name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="due">Due</label>
            <input
              id="due"
              type="datetime-local"
              value={dueAt}
              onChange={(e) => setDueAt(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="grid-2">
          <div className="field">
            <label htmlFor="title">Title</label>
            <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="max">Max score</label>
            <input
              id="max"
              type="number"
              min={1}
              step={0.5}
              value={maxScore}
              onChange={(e) => setMaxScore(Number(e.target.value))}
              required
            />
          </div>
        </div>
        <div className="field">
          <label htmlFor="desc">Brief</label>
          <textarea
            id="desc"
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What students should submit"
          />
        </div>
        <button className="btn btn-primary" type="submit" disabled={saving || !offeringId}>
          {saving ? 'Publishing…' : 'Publish assignment'}
        </button>
      </form>

      <section className="panel" style={{ marginTop: 18 }}>
        <h3 style={{ marginTop: 0 }}>Your assignments</h3>
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Course</th>
                <th>Title</th>
                <th>Due</th>
                <th>Submitted</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {assignments.map((row) => (
                <tr key={row.assignment_id}>
                  <td>{row.sub_code}</td>
                  <td>{row.title}</td>
                  <td>{new Date(row.due_at).toLocaleString()}</td>
                  <td>
                    {row.submission_count}/{row.roster_count}
                  </td>
                  <td>
                    <button
                      className="btn btn-ghost btn-tiny"
                      type="button"
                      onClick={() => setSelectedId(row.assignment_id)}
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
              {!assignments.length ? (
                <tr>
                  <td colSpan={5} className="empty">
                    No assignments yet for this course.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      {selectedId ? (
        <section className="panel" style={{ marginTop: 18 }}>
          <h3 style={{ marginTop: 0 }}>Submissions</h3>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Work</th>
                  <th>Score</th>
                  <th>Feedback</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((row) => (
                  <tr key={row.submission_id}>
                    <td>
                      {row.student_name}
                      <div style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>{row.enroll_no}</div>
                    </td>
                    <td style={{ maxWidth: 280, whiteSpace: 'pre-wrap' }}>{row.content}</td>
                    <td>
                      <input
                        type="number"
                        min={0}
                        step={0.5}
                        value={gradeDraft[row.submission_id]?.score ?? ''}
                        onChange={(e) =>
                          setGradeDraft((prev) => ({
                            ...prev,
                            [row.submission_id]: {
                              score: e.target.value,
                              feedback: prev[row.submission_id]?.feedback || '',
                            },
                          }))
                        }
                        style={{ width: 80 }}
                      />
                    </td>
                    <td>
                      <input
                        value={gradeDraft[row.submission_id]?.feedback ?? ''}
                        onChange={(e) =>
                          setGradeDraft((prev) => ({
                            ...prev,
                            [row.submission_id]: {
                              score: prev[row.submission_id]?.score || '',
                              feedback: e.target.value,
                            },
                          }))
                        }
                      />
                    </td>
                    <td>
                      <button
                        className="btn btn-primary btn-tiny"
                        type="button"
                        onClick={() => gradeOne(row.submission_id)}
                      >
                        Save grade
                      </button>
                    </td>
                  </tr>
                ))}
                {!submissions.length ? (
                  <tr>
                    <td colSpan={5} className="empty">
                      No submissions yet.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </AppShell>
  )
}
