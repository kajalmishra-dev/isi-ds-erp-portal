import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../../components/AppShell'
import { api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type Subject = {
  sub_id: string
  sub_code: string
  sub_name: string
  max_marks: number
  semester: number | null
}

export function SubjectsPage() {
  const { token } = useAuth()
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [form, setForm] = useState({ sub_code: '', sub_name: '', max_marks: 100, semester: 1 })
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function load() {
    if (!token) return
    setSubjects(await api.get<Subject[]>('/api/admin/subjects', token))
  }

  useEffect(() => {
    load().catch((err) => setError(err instanceof Error ? err.message : 'Failed to load subjects'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!token) return
    setError('')
    setMessage('')
    try {
      await api.post('/api/admin/subjects', token, form)
      setMessage('Subject created.')
      setForm({ sub_code: '', sub_name: '', max_marks: 100, semester: 1 })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create subject')
    }
  }

  return (
    <AppShell title="Subjects" subtitle="Curriculum codes, ceilings, and semester mapping.">
      <div className="grid-2">
        <form className="panel stack" onSubmit={onSubmit}>
          <h3 style={{ margin: 0 }}>Add subject</h3>
          <div className="form-grid">
            <div className="field">
              <label htmlFor="sub_code">Code</label>
              <input
                id="sub_code"
                value={form.sub_code}
                onChange={(e) => setForm((p) => ({ ...p, sub_code: e.target.value }))}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="max_marks">Max marks</label>
              <input
                id="max_marks"
                type="number"
                min={1}
                value={form.max_marks}
                onChange={(e) => setForm((p) => ({ ...p, max_marks: Number(e.target.value) }))}
                required
              />
            </div>
            <div className="field full">
              <label htmlFor="sub_name">Name</label>
              <input
                id="sub_name"
                value={form.sub_name}
                onChange={(e) => setForm((p) => ({ ...p, sub_name: e.target.value }))}
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
          </div>
          {error ? <div className="toast error">{error}</div> : null}
          {message ? <div className="toast success">{message}</div> : null}
          <button className="btn btn-primary" type="submit">
            Create subject
          </button>
        </form>

        <section className="panel">
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>Max</th>
                  <th>Sem</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {subjects.map((subject) => (
                  <tr key={subject.sub_id}>
                    <td>{subject.sub_code}</td>
                    <td>{subject.sub_name}</td>
                    <td>{subject.max_marks}</td>
                    <td>{subject.semester}</td>
                    <td>
                      <button
                        className="btn btn-danger btn-tiny"
                        type="button"
                        onClick={async () => {
                          if (!token) return
                          if (!window.confirm(`Delete subject ${subject.sub_code}? Related marks will be removed.`)) return
                          try {
                            const res = await api.delete<{ message: string }>(
                              `/api/admin/subjects/${subject.sub_id}`,
                              token,
                            )
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
