import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../../components/AppShell'
import { api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type Exam = {
  exam_id: string
  exam_name: string
  year: number
  semester: number | null
  is_active: boolean
}

export function ExamsPage() {
  const { token } = useAuth()
  const [exams, setExams] = useState<Exam[]>([])
  const [form, setForm] = useState({ exam_name: '', year: 2026, semester: 1, is_active: true })
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function load() {
    if (!token) return
    setExams(await api.get<Exam[]>('/api/admin/exams', token))
  }

  useEffect(() => {
    load().catch((err) => setError(err instanceof Error ? err.message : 'Failed to load exams'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!token) return
    setError('')
    setMessage('')
    try {
      await api.post('/api/admin/exams', token, form)
      setMessage('Exam created.')
      setForm({ exam_name: '', year: 2026, semester: 1, is_active: true })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create exam')
    }
  }

  return (
    <AppShell title="Exams" subtitle="Define assessment windows by year and semester.">
      <div className="grid-2">
        <form className="panel stack" onSubmit={onSubmit}>
          <h3 style={{ margin: 0 }}>Create exam</h3>
          <div className="form-grid">
            <div className="field full">
              <label htmlFor="exam_name">Exam name</label>
              <input
                id="exam_name"
                value={form.exam_name}
                onChange={(e) => setForm((p) => ({ ...p, exam_name: e.target.value }))}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="year">Year</label>
              <input
                id="year"
                type="number"
                value={form.year}
                onChange={(e) => setForm((p) => ({ ...p, year: Number(e.target.value) }))}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="semester">Semester</label>
              <input
                id="semester"
                type="number"
                min={1}
                max={12}
                value={form.semester}
                onChange={(e) => setForm((p) => ({ ...p, semester: Number(e.target.value) }))}
                required
              />
            </div>
            <div className="field full" style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
              <input
                id="is_active"
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm((p) => ({ ...p, is_active: e.target.checked }))}
              />
              <label htmlFor="is_active" style={{ textTransform: 'none', letterSpacing: 0 }}>
                Active for student marksheets
              </label>
            </div>
          </div>
          {error ? <div className="toast error">{error}</div> : null}
          {message ? <div className="toast success">{message}</div> : null}
          <button className="btn btn-primary" type="submit">
            Create exam
          </button>
        </form>

        <section className="panel">
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Year</th>
                  <th>Semester</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {exams.map((exam) => (
                  <tr key={exam.exam_id}>
                    <td>{exam.exam_name}</td>
                    <td>{exam.year}</td>
                    <td>{exam.semester}</td>
                    <td>
                      <span className={`badge ${exam.is_active ? 'ok' : 'fail'}`}>
                        {exam.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-danger btn-tiny"
                        type="button"
                        onClick={async () => {
                          if (!token) return
                          if (!window.confirm(`Delete exam "${exam.exam_name}" and related marks?`)) return
                          try {
                            const res = await api.delete<{ message: string }>(`/api/admin/exams/${exam.exam_id}`, token)
                            setMessage(res.message)
                            await load()
                          } catch (err) {
                            setError(err instanceof Error ? err.message : 'Delete failed')
                          }
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </AppShell>
  )
}
