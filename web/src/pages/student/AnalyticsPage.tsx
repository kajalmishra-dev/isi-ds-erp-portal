import { useEffect, useState } from 'react'
import { AppShell } from '../../components/AppShell'
import { ApiError, api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type StudentAnalytics = {
  student_name: string
  enroll_no: string
  semester: number
  exam_summaries: { exam: string; percentage: number; grade: string; result: string }[]
  subject_marks: {
    exam: string
    sub_code: string
    sub_name: string
    obtained: number
    max: number
    percentage: number
    grade: string
  }[]
  attendance: {
    offering_id: string
    sub_code: string
    sub_name: string
    sessions: number
    present: number
    percentage: number
  }[]
  overall_attendance_pct: number | null
  assignments: { open: number; submitted: number; graded: number; overdue: number; total: number }
}

function Bar({ value, label }: { value: number; label: string }) {
  return (
    <div className="bar-row">
      <div className="bar-meta">
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
    </div>
  )
}

export function StudentAnalyticsPage() {
  const { token, logout } = useAuth()
  const [data, setData] = useState<StudentAnalytics | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) return
    api
      .get<StudentAnalytics>('/api/student/analytics', token)
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
    <AppShell title="My analytics" subtitle="Your marks, attendance, and assignment progress.">
      {error ? <div className="toast error">{error}</div> : null}
      <div className="stat-grid">
        <div className="stat-card">
          <span>Attendance</span>
          <strong>
            {data?.overall_attendance_pct != null ? `${data.overall_attendance_pct}%` : '—'}
          </strong>
        </div>
        <div className="stat-card">
          <span>Open tasks</span>
          <strong>{data?.assignments.open ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Submitted</span>
          <strong>{data?.assignments.submitted ?? '—'}</strong>
        </div>
        <div className="stat-card">
          <span>Graded</span>
          <strong>{data?.assignments.graded ?? '—'}</strong>
        </div>
      </div>

      <div className="grid-2" style={{ marginTop: 18 }}>
        <section className="panel">
          <h3 style={{ marginTop: 0 }}>Exam results</h3>
          {(data?.exam_summaries ?? []).map((row) => (
            <div key={row.exam} style={{ marginBottom: 14 }}>
              <Bar value={row.percentage} label={`${row.exam} · ${row.grade}`} />
              <span className={`badge ${row.result === 'PASS' ? 'ok' : 'fail'}`}>{row.result}</span>
            </div>
          ))}
          {!data?.exam_summaries?.length ? <div className="empty">No exam marks yet.</div> : null}
        </section>

        <section className="panel">
          <h3 style={{ marginTop: 0 }}>Attendance by subject</h3>
          {(data?.attendance ?? []).map((row) => (
            <Bar
              key={row.offering_id}
              value={row.percentage}
              label={`${row.sub_code} · ${row.present}/${row.sessions}`}
            />
          ))}
          {!data?.attendance?.length ? <div className="empty">No attendance yet.</div> : null}
        </section>
      </div>
    </AppShell>
  )
}
