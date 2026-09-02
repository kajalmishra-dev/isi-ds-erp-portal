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
    <AppShell title="Faculty desk" subtitle="Your course offerings and recent attendance activity.">
      {error ? <div className="toast error">{error}</div> : null}
      <div className="stat-grid">
        <div className="stat-card">
          <span>Courses this term</span>
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
          <strong style={{ fontSize: '1.1rem' }}>{dash?.department ?? '—'}</strong>
        </div>
      </div>

      <section className="panel" style={{ marginTop: 18 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
          <div>
            <h3 style={{ margin: '0 0 6px' }}>{dash?.faculty_name ?? 'Faculty'}</h3>
            <div style={{ color: 'var(--muted)' }}>Employee {dash?.employee_code}</div>
          </div>
          <Link className="btn btn-primary" to="/faculty/attendance">
            Take attendance
          </Link>
          <Link className="btn btn-ghost" to="/faculty/assignments">
            Assignments
          </Link>
          <Link className="btn btn-ghost" to="/faculty/notices">
            Notices
          </Link>
        </div>
        <div className="table-wrap" style={{ marginTop: 16 }}>
          <table className="data">
            <thead>
              <tr>
                <th>Code</th>
                <th>Subject</th>
                <th>Semester</th>
                <th>Term</th>
                <th>Sessions</th>
                <th>Roster</th>
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
                    No course offerings assigned yet.
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
