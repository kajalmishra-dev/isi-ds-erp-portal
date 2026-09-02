import { useEffect, useState } from 'react'
import { AppShell } from '../../components/AppShell'
import { ApiError, api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type AdminAnalytics = {
  totals: {
    students: number
    exams: number
    subjects: number
    marks: number
    assignments: number
    submissions: number
    graded_submissions: number
    attendance_sessions: number
  }
  students_by_semester: { semester: number; count: number }[]
  subject_averages: { label: string; average_pct: number; entries: number }[]
  results: { pass_entries: number; fail_entries: number; pass_rate_pct: number | null }
  attendance_pct: number | null
  graded_rate_pct: number | null
}

function Bar({ value, label }: { value: number; label: string }) {
  const width = Math.max(0, Math.min(100, value))
  return (
    <div className="bar-row">
      <div className="bar-meta">
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${width}%` }} />
      </div>
    </div>
  )
}

export function AdminAnalyticsPage() {
  const { token, logout } = useAuth()
  const [data, setData] = useState<AdminAnalytics | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    api
      .get<AdminAnalytics>('/api/admin/analytics', token)
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

  const maxSemester = Math.max(1, ...(data?.students_by_semester.map((s) => s.count) ?? [1]))

  return (
    <AppShell title="Analytics" subtitle="Programme aggregates from marks, attendance, and coursework.">
      {error ? <div className="toast error">{error}</div> : null}
      <div className="stat-grid">
        <div className="stat-card">
          <span>Students</span>
          <strong>{data?.totals.students ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Pass rate</span>
          <strong>
            {data?.results.pass_rate_pct != null ? `${data.results.pass_rate_pct}%` : '—'}
          </strong>
        </div>
        <div className="stat-card">
          <span>Attendance</span>
          <strong>{data?.attendance_pct != null ? `${data.attendance_pct}%` : '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Graded work</span>
          <strong>{data?.graded_rate_pct != null ? `${data.graded_rate_pct}%` : '—'}</strong>
        </div>
      </div>

      <div className="grid-2" style={{ marginTop: 18 }}>
        <section className="panel">
          <h3 style={{ marginTop: 0 }}>Students by semester</h3>
          {(data?.students_by_semester ?? []).map((row) => (
            <div className="bar-row" key={row.semester}>
              <div className="bar-meta">
                <span>Semester {row.semester}</span>
                <strong>{row.count}</strong>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${Math.round((row.count / maxSemester) * 100)}%` }}
                />
              </div>
            </div>
          ))}
          {!data?.students_by_semester?.length ? <div className="empty">No enrollment data.</div> : null}
        </section>

        <section className="panel">
          <h3 style={{ marginTop: 0 }}>Subject averages</h3>
          {(data?.subject_averages ?? []).map((row) => (
            <Bar key={row.label} value={row.average_pct} label={row.label} />
          ))}
          {!data?.subject_averages?.length ? <div className="empty">No marks yet.</div> : null}
        </section>
      </div>

      <section className="panel" style={{ marginTop: 18 }}>
        <h3 style={{ marginTop: 0 }}>Volume</h3>
        <div className="stat-grid">
          <div className="stat-card">
            <span>Marks posted</span>
            <strong>{data?.totals.marks ?? '—'}</strong>
          </div>
          <div className="stat-card">
            <span>Assignments</span>
            <strong>{data?.totals.assignments ?? '—'}</strong>
          </div>
          <div className="stat-card">
            <span>Submissions</span>
            <strong>{data?.totals.submissions ?? '—'}</strong>
          </div>
          <div className="stat-card">
            <span>Attendance sessions</span>
            <strong>{data?.totals.attendance_sessions ?? '—'}</strong>
          </div>
        </div>
      </section>
    </AppShell>
  )
}
