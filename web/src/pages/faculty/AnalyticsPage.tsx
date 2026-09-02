import { useEffect, useState } from 'react'
import { AppShell } from '../../components/AppShell'
import { ApiError, api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type CourseRow = {
  offering_id: string
  sub_code: string
  sub_name: string
  roster_count: number
  session_count: number
  attendance_pct: number | null
  assignment_count: number
  submission_count: number
  graded_count: number
  submission_rate_pct: number | null
  avg_score_pct: number | null
}

type FacultyAnalytics = {
  faculty_name: string
  courses: CourseRow[]
  totals: { courses: number; students: number; sessions: number; assignments: number }
}

export function FacultyAnalyticsPage() {
  const { token, logout } = useAuth()
  const [data, setData] = useState<FacultyAnalytics | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    api
      .get<FacultyAnalytics>('/api/faculty/analytics', token)
      .then(setData)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          logout()
          window.location.assign('/login')
          return
        }
        setError(err instanceof Error ? err.message : 'Failed to load analytics')
      })
  }, [token, logout])

  return (
    <AppShell title="Course analytics" subtitle="Attendance and coursework signals for your offerings.">
      {error ? <div className="toast error">{error}</div> : null}
      <div className="stat-grid">
        <div className="stat-card">
          <span>Courses</span>
          <strong>{data?.totals.courses ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Students</span>
          <strong>{data?.totals.students ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Sessions</span>
          <strong>{data?.totals.sessions ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Assignments</span>
          <strong>{data?.totals.assignments ?? '—'}</strong>
        </div>
      </div>

      <section className="panel" style={{ marginTop: 18 }}>
        <h3 style={{ marginTop: 0 }}>{data?.faculty_name ?? 'Faculty'} · offerings</h3>
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Course</th>
                <th>Roster</th>
                <th>Attendance</th>
                <th>Submissions</th>
                <th>Avg score</th>
              </tr>
            </thead>
            <tbody>
              {(data?.courses ?? []).map((row) => (
                <tr key={row.offering_id}>
                  <td>
                    {row.sub_code}
                    <div style={{ color: 'var(--muted)', fontSize: '0.82rem' }}>{row.sub_name}</div>
                  </td>
                  <td>{row.roster_count}</td>
                  <td>
                    {row.attendance_pct != null ? `${row.attendance_pct}%` : '—'}
                    <div style={{ color: 'var(--muted)', fontSize: '0.82rem' }}>
                      {row.session_count} sessions
                    </div>
                  </td>
                  <td>
                    {row.submission_count}/{row.assignment_count * row.roster_count || 0}
                    <div style={{ color: 'var(--muted)', fontSize: '0.82rem' }}>
                      {row.submission_rate_pct != null ? `${row.submission_rate_pct}% rate` : '—'}
                    </div>
                  </td>
                  <td>{row.avg_score_pct != null ? `${row.avg_score_pct}%` : '—'}</td>
                </tr>
              ))}
              {!data?.courses?.length ? (
                <tr>
                  <td colSpan={5} className="empty">
                    No course offerings yet.
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
