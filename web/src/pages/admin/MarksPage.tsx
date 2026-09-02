import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../../components/AppShell'
import { api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type Student = { std_id: string; enroll_no: string; first_name: string; last_name: string }
type Exam = { exam_id: string; exam_name: string; year: number; semester: number | null }
type Subject = { sub_id: string; sub_code: string; sub_name: string; max_marks: number }
type RecentMark = {
  mark_id: string
  student_name?: string
  enroll_no?: string
  exam_name?: string
  subject_code?: string
  marks_obtained: number
}

export function MarksPage() {
  const { token } = useAuth()
  const [students, setStudents] = useState<Student[]>([])
  const [exams, setExams] = useState<Exam[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [recent, setRecent] = useState<RecentMark[]>([])
  const [form, setForm] = useState({ std_id: '', exam_id: '', sub_id: '', marks_obtained: 0 })
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const selectedSubject = useMemo(
    () => subjects.find((s) => s.sub_id === form.sub_id),
    [subjects, form.sub_id],
  )

  async function refresh() {
    if (!token) return
    const [studentList, examList, subjectList, recentMarks] = await Promise.all([
      api.get<{ data: Student[] }>('/api/admin/students?page=1&limit=100', token),
      api.get<Exam[]>('/api/admin/exams', token),
      api.get<Subject[]>('/api/admin/subjects', token),
      api.get<RecentMark[]>('/api/admin/marks/recent?limit=20', token),
    ])
    setStudents(studentList.data)
    setExams(examList)
    setSubjects(subjectList)
    setRecent(recentMarks)
    setForm((prev) => ({
      ...prev,
      std_id: prev.std_id || studentList.data[0]?.std_id || '',
      exam_id: prev.exam_id || examList[0]?.exam_id || '',
      sub_id: prev.sub_id || subjectList[0]?.sub_id || '',
    }))
  }

  useEffect(() => {
    refresh().catch((err) => setError(err instanceof Error ? err.message : 'Failed to load mark form'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!token) return
    setError('')
    setMessage('')
    try {
      await api.post('/api/admin/marks', token, {
        ...form,
        marks_obtained: Number(form.marks_obtained),
      })
      setMessage('Marks saved (create or update).')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save marks')
    }
  }

  return (
    <AppShell title="Marks entry" subtitle="Post, correct, or delete scores against the subject ceiling.">
      <div className="grid-2">
        <form className="panel stack" onSubmit={onSubmit}>
          <div className="form-grid">
            <div className="field full">
              <label htmlFor="std_id">Student</label>
              <select
                id="std_id"
                value={form.std_id}
                onChange={(e) => setForm((p) => ({ ...p, std_id: e.target.value }))}
                required
              >
                {students.map((s) => (
                  <option key={s.std_id} value={s.std_id}>
                    {s.enroll_no} — {s.first_name} {s.last_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="exam_id">Exam</label>
              <select
                id="exam_id"
                value={form.exam_id}
                onChange={(e) => setForm((p) => ({ ...p, exam_id: e.target.value }))}
                required
              >
                {exams.map((e) => (
                  <option key={e.exam_id} value={e.exam_id}>
                    {e.exam_name} ({e.year})
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="sub_id">Subject</label>
              <select
                id="sub_id"
                value={form.sub_id}
                onChange={(e) => setForm((p) => ({ ...p, sub_id: e.target.value }))}
                required
              >
                {subjects.map((s) => (
                  <option key={s.sub_id} value={s.sub_id}>
                    {s.sub_code} — {s.sub_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="marks_obtained">
                Marks obtained{selectedSubject ? ` / ${selectedSubject.max_marks}` : ''}
              </label>
              <input
                id="marks_obtained"
                type="number"
                min={0}
                max={selectedSubject?.max_marks ?? 1000}
                value={form.marks_obtained}
                onChange={(e) => setForm((p) => ({ ...p, marks_obtained: Number(e.target.value) }))}
                required
              />
            </div>
          </div>
          {error ? <div className="toast error">{error}</div> : null}
          {message ? <div className="toast success">{message}</div> : null}
          <button className="btn btn-primary" type="submit">
            Save marks
          </button>
        </form>

        <section className="panel">
          <h3 style={{ marginTop: 0 }}>Recent entries</h3>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Exam / Subject</th>
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
                    <td>
                      {row.exam_name}
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
                            const res = await api.delete<{ message: string }>(
                              `/api/admin/marks/${row.mark_id}`,
                              token,
                            )
                            setMessage(res.message)
                            await refresh()
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
                    <td colSpan={4} className="empty">
                      No marks yet.
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
