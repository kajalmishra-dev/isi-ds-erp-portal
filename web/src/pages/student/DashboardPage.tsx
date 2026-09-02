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
    <AppShell title="Student desk" subtitle="Semester snapshot — attendance, exams, and marksheet access.">
      {error ? <div className="toast error">{error}</div> : null}

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
          <span>Marks on record</span>
          <strong>{dash?.mark_count ?? '—'}</strong>
        </div>
      </div>

      <div className="grid-2" style={{ marginTop: 18 }}>
        <section className="panel">
          <h3 style={{ marginTop: 0 }}>{dash?.student_name ?? 'Student'}</h3>
          <p style={{ color: 'var(--muted)', marginTop: 0 }}>
            Enroll {dash?.enroll_no ?? '—'} · Semester {dash?.semester ?? '—'}
          </p>
          <Link className="btn btn-primary" to="/student/marksheet">
            Open marksheet
          </Link>
          <Link className="btn btn-ghost" to="/student/assignments" style={{ marginLeft: 8 }}>
            Assignments
          </Link>
          <Link className="btn btn-ghost" to="/student/notices" style={{ marginLeft: 8 }}>
            Notices
          </Link>
        </section>

        <section className="panel">
          <h3 style={{ marginTop: 0 }}>Attendance by subject</h3>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Subject</th>
                  <th>Present</th>
                  <th>%</th>
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
                    <td>{row.percentage}%</td>
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
      </div>
    </AppShell>
  )
}
