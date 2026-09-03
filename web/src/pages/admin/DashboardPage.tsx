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
    <AppShell
      title="Admin overview"
      subtitle="Start here — enroll students, create exams, then post marks."
    >
      {error ? <div className="toast error">{error}</div> : null}

      <div className="guide-banner">
        <div>
          <strong>Suggested order</strong>
          <p>1) Students → 2) Subjects → 3) Exams → 4) Marks → 5) Notices</p>
        </div>
      </div>

      <div className="action-tiles">
        <Link className="action-tile" to="/admin/students">
          <strong>Students</strong>
          <span>Add or edit the roster</span>
        </Link>
        <Link className="action-tile" to="/admin/exams">
          <strong>Exams</strong>
          <span>Create an exam session</span>
        </Link>
        <Link className="action-tile" to="/admin/marks">
          <strong>Marks</strong>
          <span>Enter scores on marksheets</span>
        </Link>
        <Link className="action-tile" to="/admin/notices">
          <strong>Notices</strong>
          <span>Publish a campus message</span>
        </Link>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <span>Students</span>
          <strong>{stats?.total_students ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Exams</span>
          <strong>{stats?.total_exams ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Subjects</span>
          <strong>{stats?.total_subjects ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Marks posted</span>
          <strong>{stats?.total_marks ?? '—'}</strong>
        </div>
      </div>

      <section className="panel" style={{ marginTop: 18 }}>
        <h3 style={{ marginTop: 0 }}>Latest marks posted</h3>
        <p className="panel-help">Most recent result entries — delete only if entered by mistake.</p>
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
                    <div className="cell-meta">{row.enroll_no}</div>
                  </td>
                  <td>{row.exam_name}</td>
                  <td>
                    {row.subject_name}
                    <div className="cell-meta">{row.subject_code}</div>
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
                    No marks recorded yet. Open Marks to post the first score.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </AppShell>
  )
}
