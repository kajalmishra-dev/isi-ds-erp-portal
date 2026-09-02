import { useEffect, useState } from 'react'
import { AppShell } from '../components/AppShell'
import { ApiError, api } from '../lib/api'
import { useAuth } from '../lib/auth'

type Exam = {
  exam_id: string
  exam_name: string
  year: number
  semester: number | null
}

type Marksheet = {
  student: { enroll_no: string; name: string; semester: number; email: string }
  exam: { name: string; year: number; semester: number | null }
  marks: { subject: string; code: string; obtained: number; max: number }[]
  summary: {
    total_obtained: number
    total_max: number
    percentage: number
    grade: string
    result: string
  }
}

export function StudentMarksheetPage() {
  const { token, logout } = useAuth()
  const [exams, setExams] = useState<Exam[]>([])
  const [examId, setExamId] = useState('')
  const [sheet, setSheet] = useState<Marksheet | null>(null)
  const [error, setError] = useState('')
  const [downloading, setDownloading] = useState(false)

  function handleAuthError(err: unknown) {
    if (err instanceof ApiError && err.status === 401) {
      logout()
      window.location.assign('/login')
      return true
    }
    return false
  }

  useEffect(() => {
    if (!token) return
    api
      .get<Exam[]>('/api/student/exams', token)
      .then((data) => {
        setExams(data)
        if (data[0]) setExamId(data[0].exam_id)
      })
      .catch((err) => {
        if (handleAuthError(err)) return
        setError(err instanceof Error ? err.message : 'Failed to load exams')
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  useEffect(() => {
    if (!token || !examId) return
    setError('')
    api
      .get<Marksheet>(`/api/student/marksheet?exam_id=${examId}`, token)
      .then(setSheet)
      .catch((err) => {
        if (handleAuthError(err)) return
        setSheet(null)
        setError(err instanceof Error ? err.message : 'Failed to load marksheet')
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, examId])

  async function downloadPdf() {
    if (!token || !examId || !sheet) return
    setDownloading(true)
    setError('')
    try {
      const filename = `Marksheet_${sheet.student.enroll_no}_${sheet.exam.name.replace(/\s+/g, '_')}.pdf`
      await api.download(`/api/student/marksheet/pdf?exam_id=${examId}`, token, filename)
    } catch (err) {
      if (handleAuthError(err)) return
      setError(err instanceof Error ? err.message : 'PDF download failed')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <AppShell title="My marksheet" subtitle="Select an examination to view scores and download the official PDF.">
      <section className="panel stack">
        <div className="field" style={{ maxWidth: 420 }}>
          <label htmlFor="exam">Examination</label>
          <select id="exam" value={examId} onChange={(e) => setExamId(e.target.value)}>
            {exams.map((exam) => (
              <option key={exam.exam_id} value={exam.exam_id}>
                {exam.exam_name} · {exam.year}
              </option>
            ))}
          </select>
        </div>

        {error ? <div className="toast error">{error}</div> : null}

        {sheet ? (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
              <div>
                <h3 style={{ margin: '0 0 6px', fontFamily: 'var(--display)', fontWeight: 500 }}>
                  {sheet.student.name}
                </h3>
                <div style={{ color: 'var(--muted)' }}>
                  Enroll {sheet.student.enroll_no} · Semester {sheet.student.semester} · {sheet.exam.name}{' '}
                  {sheet.exam.year}
                </div>
              </div>
              <div className="marksheet-actions">
                <button className="btn btn-primary" type="button" onClick={downloadPdf} disabled={downloading}>
                  {downloading ? 'Preparing PDF…' : 'Download official PDF'}
                </button>
              </div>
            </div>

            <div className="certificate-preview">
              <div className="certificate-header">
                <strong>Meridian Institute of Computing</strong>
                <span>B.Tech CS & AI · Official Statement of Marks</span>
              </div>
              <div className="marksheet-summary">
                <div className="stat-card">
                  <span>Total</span>
                  <strong>
                    {sheet.summary.total_obtained}/{sheet.summary.total_max}
                  </strong>
                </div>
                <div className="stat-card">
                  <span>Percentage</span>
                  <strong>{sheet.summary.percentage}%</strong>
                </div>
                <div className="stat-card">
                  <span>Grade</span>
                  <strong>{sheet.summary.grade}</strong>
                </div>
                <div className="stat-card">
                  <span>Result</span>
                  <strong>
                    <span className={`badge ${sheet.summary.result === 'PASS' ? 'ok' : 'fail'}`}>
                      {sheet.summary.result}
                    </span>
                  </strong>
                </div>
              </div>
              <div className="table-wrap">
                <table className="data">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Code</th>
                      <th>Obtained</th>
                      <th>Max</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sheet.marks.map((row) => (
                      <tr key={row.code}>
                        <td>{row.subject}</td>
                        <td>{row.code}</td>
                        <td>{row.obtained}</td>
                        <td>{row.max}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : null}
      </section>
    </AppShell>
  )
}
