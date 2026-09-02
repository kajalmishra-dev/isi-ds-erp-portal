import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../../components/AppShell'
import { api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type Student = {
  std_id: string
  enroll_no: string
  first_name: string
  last_name: string
  email: string
  semester: number
}

type StudentList = {
  total: number
  page: number
  limit: number
  data: Student[]
}

const emptyForm = {
  username: '',
  password: '',
  enroll_no: '',
  first_name: '',
  last_name: '',
  email: '',
  semester: 1,
}

export function StudentsPage() {
  const { token } = useAuth()
  const [form, setForm] = useState(emptyForm)
  const [search, setSearch] = useState('')
  const [list, setList] = useState<StudentList | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function load(term = search) {
    if (!token) return
    const data = await api.get<StudentList>(
      `/api/admin/students?search=${encodeURIComponent(term)}&page=1&limit=50`,
      token,
    )
    setList(data)
  }

  useEffect(() => {
    load().catch((err) => setError(err instanceof Error ? err.message : 'Failed to load students'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!token) return
    setSaving(true)
    setError('')
    setMessage('')
    try {
      await api.post('/api/admin/students', token, form)
      setForm(emptyForm)
      setMessage('Student enrolled successfully.')
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create student')
    } finally {
      setSaving(false)
    }
  }

  async function removeStudent(student: Student) {
    if (!token) return
    if (!window.confirm(`Remove ${student.first_name} ${student.last_name} (${student.enroll_no})? This deletes their login and marks.`)) {
      return
    }
    setError('')
    try {
      const res = await api.delete<{ message: string }>(`/api/admin/students/${student.std_id}`, token)
      setMessage(res.message)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  async function resetPassword(student: Student) {
    if (!token) return
    const pwd = window.prompt(`New temporary password for ${student.enroll_no}`, 'student123')
    if (!pwd) return
    setError('')
    try {
      const res = await api.post<{ message: string }>(
        `/api/admin/students/${student.std_id}/reset-password`,
        token,
        { new_password: pwd },
      )
      setMessage(res.message)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Password reset failed')
    }
  }

  return (
    <AppShell title="Student roster" subtitle="Enroll learners, reset campus passwords, or remove records.">
      <div className="grid-2">
        <form className="panel stack" onSubmit={onSubmit}>
          <h3 style={{ margin: 0 }}>Enroll student</h3>
          <div className="form-grid">
            {(
              [
                ['username', 'Username'],
                ['password', 'Password'],
                ['enroll_no', 'Enroll no'],
                ['first_name', 'First name'],
                ['last_name', 'Last name'],
                ['email', 'Email'],
              ] as const
            ).map(([key, label]) => (
              <div className="field" key={key}>
                <label htmlFor={key}>{label}</label>
                <input
                  id={key}
                  type={key === 'password' ? 'password' : key === 'email' ? 'email' : 'text'}
                  value={form[key]}
                  onChange={(e) => setForm((prev) => ({ ...prev, [key]: e.target.value }))}
                  required
                />
              </div>
            ))}
            <div className="field">
              <label htmlFor="semester">Semester</label>
              <input
                id="semester"
                type="number"
                min={1}
                max={12}
                value={form.semester}
                onChange={(e) => setForm((prev) => ({ ...prev, semester: Number(e.target.value) }))}
                required
              />
            </div>
          </div>
          {error ? <div className="toast error">{error}</div> : null}
          {message ? <div className="toast success">{message}</div> : null}
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? 'Saving…' : 'Create student'}
          </button>
        </form>

        <section className="panel">
          <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
            <input
              style={{
                flex: 1,
                borderRadius: 12,
                border: '1px solid var(--line-strong)',
                background: 'rgba(8,16,24,.7)',
                color: 'var(--text)',
                padding: '12px 14px',
              }}
              placeholder="Search enroll / name / email"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button
              className="btn btn-ghost"
              type="button"
              onClick={() =>
                load().catch((err) => setError(err instanceof Error ? err.message : 'Search failed'))
              }
            >
              Search
            </button>
          </div>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Enroll</th>
                  <th>Name</th>
                  <th>Sem</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {list?.data.map((s) => (
                  <tr key={s.std_id}>
                    <td>
                      {s.enroll_no}
                      <div style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>{s.email}</div>
                    </td>
                    <td>
                      {s.first_name} {s.last_name}
                    </td>
                    <td>{s.semester}</td>
                    <td>
                      <div className="row-actions">
                        <button className="btn btn-ghost btn-tiny" type="button" onClick={() => resetPassword(s)}>
                          Reset pwd
                        </button>
                        <button className="btn btn-danger btn-tiny" type="button" onClick={() => removeStudent(s)}>
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {!list?.data.length ? (
                  <tr>
                    <td colSpan={4} className="empty">
                      No students found.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
          <p style={{ color: 'var(--muted)', marginBottom: 0 }}>Total: {list?.total ?? 0}</p>
        </section>
      </div>
    </AppShell>
  )
}
