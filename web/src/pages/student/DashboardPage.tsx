import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AppShell } from '../../components/AppShell'
import { ApiError, api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type AttendanceRow = {
  offering_id: string
  sub_code: string
  sub_name: string
  sessions: number
  present: number
  percentage: number
}

type Dashboard = {
  student_name: string
  enroll_no: string
  semester: number
  exam_count: number
  mark_count: number
  attendance: AttendanceRow[]
  overall_attendance_pct: number | null
}

function pctBadge(pct: number) {
  if (pct >= 75) return 'ok'
  if (pct >= 60) return 'warn'
  return 'fail'
}

export function StudentDashboardPage() {
  const { token, logout } = useAuth()
  const [dash, setDash] = useState<Dashboard | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    api
      .get<Dashboard>('/api/student/dashboard', token)
      .then(setDash)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          logout()
          window.location.assign('/login')
          return
        }
        setError(err instanceof Error ? err.message : 'Failed to load dashboard')
      })
  }, [token, logout])

  return (
    <AppShell
      title="Your overview"
      subtitle="Quick view of this semester — then jump to assignments or marksheet."
    >
      {error ? <div className="toast error">{error}</div> : null}

      <div className="guide-banner">
        <div>
          <strong>Hi {dash?.student_name ?? 'there'}</strong>
          <p>
            Enroll <code>{dash?.enroll_no ?? '—'}</code> · Semester {dash?.semester ?? '—'}
          </p>
        </div>
      </div>

      <div className="action-tiles">
        <Link className="action-tile" to="/student/assignments">
          <strong>Assignments</strong>
          <span>Submit lab / homework work</span>
        </Link>
        <Link className="action-tile" to="/student/marksheet">
          <strong>Marksheet</strong>
          <span>View scores & download PDF</span>
        </Link>
        <Link className="action-tile" to="/student/notices">
          <strong>Notices</strong>
          <span>Campus announcements</span>
        </Link>
        <Link className="action-tile" to="/student/analytics">
          <strong>My analytics</strong>
          <span>Charts for attendance & marks</span>
        </Link>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <span>Semester</span>
          <strong>{dash?.semester ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Overall attendance</span>
          <strong>
            {dash?.overall_attendance_pct != null ? `${dash.overall_attendance_pct}%` : '—'}
          </strong>
        </div>
        <div className="stat-card">
          <span>Active exams</span>
          <strong>{dash?.exam_count ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Marks recorded</span>
          <strong>{dash?.mark_count ?? '—'}</strong>
        </div>
      </div>

      <section className="panel" style={{ marginTop: 18 }}>
        <h3 style={{ marginTop: 0 }}>Attendance by subject</h3>
        <p className="panel-help">Green ≥ 75% · Amber 60–74% · Red below 60%</p>
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Code</th>
                <th>Subject</th>
                <th>Present</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {(dash?.attendance ?? []).map((row) => (
                <tr key={row.offering_id}>
                  <td>{row.sub_code}</td>
                  <td>{row.sub_name}</td>
                  <td>
                    {row.present}/{row.sessions}
                  </td>
                  <td>
                    <span className={`badge ${pctBadge(row.percentage)}`}>{row.percentage}%</span>
                  </td>
                </tr>
              ))}
              {!dash?.attendance?.length ? (
                <tr>
                  <td colSpan={4} className="empty">
                    No attendance recorded for your semester yet.
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
