import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AppShell } from '../../components/AppShell'
import { api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type Stats = {
  total_students: number
  total_exams: number
  total_subjects: number
  total_marks: number
}

type RecentMark = {
  mark_id: string
  student_name?: string
  enroll_no?: string
  exam_name?: string
  subject_name?: string
  subject_code?: string
  marks_obtained: number
}

export function AdminDashboardPage() {
  const { token } = useAuth()
  const [stats, setStats] = useState<Stats | null>(null)
  const [recent, setRecent] = useState<RecentMark[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    Promise.all([
      api.get<Stats>('/api/admin/dashboard', token),
      api.get<RecentMark[]>('/api/admin/marks/recent?limit=8', token),
    ])
      .then(([dashboard, marks]) => {
        setStats(dashboard)
        setRecent(marks)
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load dashboard'))
  }, [token])

  return (
    <AppShell title="Registrar desk" subtitle="Semester enrollments, examinations, subjects, and posted results.">
      {error ? <div className="toast error">{error}</div> : null}
      <div className="stat-grid">
        <div className="stat-card">
          <span>Enrolled students</span>
          <strong>{stats?.total_students ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Active exams</span>
          <strong>{stats?.total_exams ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Course subjects</span>
          <strong>{stats?.total_subjects ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Marks on record</span>
          <strong>{stats?.total_marks ?? '—'}</strong>
        </div>
      </div>

      <div className="grid-2" style={{ marginTop: 18 }}>
        <section className="panel">
          <h3 style={{ marginTop: 0 }}>Latest result postings</h3>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Exam</th>
                  <th>Subject</th>
                  <th>Marks</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {recent.map((row) => (
                  <tr key={row.mark_id}>
                    <td>
                      {row.student_name}
                      <div style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>{row.enroll_no}</div>
                    </td>
                    <td>{row.exam_name}</td>
                    <td>
                      {row.subject_name}
                      <div style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>{row.subject_code}</div>
                    </td>
                    <td>{row.marks_obtained}</td>
                    <td>
                      <button
                        className="btn btn-danger btn-tiny"
                        type="button"
                        onClick={async () => {
                          if (!token) return
                          if (!window.confirm('Delete this mark entry?')) return
                          try {
                            await api.delete(`/api/admin/marks/${row.mark_id}`, token)
                            setRecent((prev) => prev.filter((m) => m.mark_id !== row.mark_id))
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
                {!recent.length ? (
                  <tr>
                    <td colSpan={5} className="empty">
                      No marks recorded yet.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel stack">
          <h3 style={{ marginTop: 0 }}>Academic workflow</h3>
          <p style={{ margin: 0, color: 'var(--muted)' }}>
            Enroll a learner, schedule an exam, map semester subjects, then post marks to their marksheet.
          </p>
          <Link className="btn btn-primary" to="/admin/students">
            Enroll student
          </Link>
          <Link className="btn btn-ghost" to="/admin/exams">
            Schedule exam
          </Link>
          <Link className="btn btn-ghost" to="/admin/marks">
            Post marks
          </Link>
          <Link className="btn btn-ghost" to="/admin/notices">
            Publish notice
          </Link>
        </section>
      </div>
    </AppShell>
  )
}
