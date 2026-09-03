import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AppShell } from '../../components/AppShell'
import { ApiError, api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type Dashboard = {
  faculty_name: string
  employee_code: string
  department: string
  offering_count: number
  session_count: number
  student_roster_size: number
}

type Offering = {
  offering_id: string
  sub_code: string
  sub_name: string
  semester: number | null
  academic_year: number
  term: string
  session_count: number
  roster_count: number
}

export function FacultyDashboardPage() {
  const { token, logout } = useAuth()
  const [dash, setDash] = useState<Dashboard | null>(null)
  const [offerings, setOfferings] = useState<Offering[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    Promise.all([
      api.get<Dashboard>('/api/faculty/dashboard', token),
      api.get<Offering[]>('/api/faculty/offerings', token),
    ])
      .then(([dashboard, list]) => {
        setDash(dashboard)
        setOfferings(list)
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          logout()
          window.location.assign('/login')
          return
        }
        setError(err instanceof Error ? err.message : 'Failed to load faculty desk')
      })
  }, [token, logout])

  return (
    <AppShell
      title="Faculty overview"
      subtitle="Your courses this term — take attendance or open assignments."
    >
      {error ? <div className="toast error">{error}</div> : null}

      <div className="guide-banner">
        <div>
          <strong>{dash?.faculty_name ?? 'Faculty'}</strong>
          <p>
            {dash?.department ?? '—'} · Code <code>{dash?.employee_code ?? '—'}</code>
          </p>
        </div>
      </div>

      <div className="action-tiles">
        <Link className="action-tile" to="/faculty/attendance">
          <strong>Attendance</strong>
          <span>Mark who came to class</span>
        </Link>
        <Link className="action-tile" to="/faculty/assignments">
          <strong>Assignments</strong>
          <span>Publish work & grade it</span>
        </Link>
        <Link className="action-tile" to="/faculty/notices">
          <strong>Notices</strong>
          <span>Message your students</span>
        </Link>
        <Link className="action-tile" to="/faculty/analytics">
          <strong>Analytics</strong>
          <span>See course trends</span>
        </Link>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <span>Courses</span>
          <strong>{dash?.offering_count ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Attendance sessions</span>
          <strong>{dash?.session_count ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Students on roster</span>
          <strong>{dash?.student_roster_size ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Department</span>
          <strong className="stat-text">{dash?.department ?? '—'}</strong>
        </div>
      </div>

      <section className="panel" style={{ marginTop: 18 }}>
        <h3 style={{ marginTop: 0 }}>Your courses</h3>
        <p className="panel-help">Each row is a subject you teach this term.</p>
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Code</th>
                <th>Subject</th>
                <th>Sem</th>
                <th>Term</th>
                <th>Sessions</th>
                <th>Students</th>
              </tr>
            </thead>
            <tbody>
              {offerings.map((row) => (
                <tr key={row.offering_id}>
                  <td>{row.sub_code}</td>
                  <td>{row.sub_name}</td>
                  <td>{row.semester ?? '—'}</td>
                  <td>
                    {row.term} {row.academic_year}
                  </td>
                  <td>{row.session_count}</td>
                  <td>{row.roster_count}</td>
                </tr>
              ))}
              {!offerings.length ? (
                <tr>
                  <td colSpan={6} className="empty">
                    No courses assigned yet.
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
