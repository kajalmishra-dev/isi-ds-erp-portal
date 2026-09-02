import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../../components/AppShell'
import { ApiError, api } from '../../lib/api'
import { useAuth } from '../../lib/auth'

type Offering = {
  offering_id: string
  sub_code: string
  sub_name: string
  session_count: number
  roster_count: number
}

type RosterStudent = {
  std_id: string
  enroll_no: string
  name: string
  semester: number
}

type SessionOut = {
  session_id: string
  session_date: string
  topic: string | null
  records: { std_id: string; enroll_no: string; name: string; status: string }[]
}

const STATUSES = ['present', 'absent', 'late', 'excused'] as const

export function FacultyAttendancePage() {
  const { token, logout } = useAuth()
  const [offerings, setOfferings] = useState<Offering[]>([])
  const [offeringId, setOfferingId] = useState('')
  const [roster, setRoster] = useState<RosterStudent[]>([])
  const [statusMap, setStatusMap] = useState<Record<string, string>>({})
  const [sessionDate, setSessionDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [topic, setTopic] = useState('')
  const [sessions, setSessions] = useState<SessionOut[]>([])
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)

  function handleAuth(err: unknown) {
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
      .get<Offering[]>('/api/faculty/offerings', token)
      .then((list) => {
        setOfferings(list)
        if (list[0]) setOfferingId(list[0].offering_id)
      })
      .catch((err) => {
        if (handleAuth(err)) return
        setError(err instanceof Error ? err.message : 'Failed to load offerings')
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  useEffect(() => {
    if (!token || !offeringId) return
    setError('')
    Promise.all([
      api.get<RosterStudent[]>(`/api/faculty/offerings/${offeringId}/roster`, token),
      api.get<SessionOut[]>(`/api/faculty/offerings/${offeringId}/attendance`, token),
    ])
      .then(([students, history]) => {
        setRoster(students)
        setSessions(history)
        const next: Record<string, string> = {}
        for (const s of students) next[s.std_id] = 'present'
        setStatusMap(next)
      })
      .catch((err) => {
        if (handleAuth(err)) return
        setError(err instanceof Error ? err.message : 'Failed to load roster')
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, offeringId])

  const selected = useMemo(
    () => offerings.find((o) => o.offering_id === offeringId),
    [offerings, offeringId],
  )

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!token || !offeringId) return
    setSaving(true)
    setError('')
    setMessage('')
    try {
      const created = await api.post<SessionOut>(
        `/api/faculty/offerings/${offeringId}/attendance/sessions`,
        token,
        {
          session_date: sessionDate,
          topic: topic.trim() || null,
          records: roster.map((s) => ({
            std_id: s.std_id,
            status: statusMap[s.std_id] || 'present',
          })),
        },
      )
      setSessions((prev) => [created, ...prev])
      setMessage('Attendance session saved.')
      setTopic('')
    } catch (err) {
      if (handleAuth(err)) return
      setError(err instanceof Error ? err.message : 'Could not save attendance')
    } finally {
      setSaving(false)
    }
  }

  return (
    <AppShell title="Attendance" subtitle="Mark a class session for one of your course offerings.">
      {error ? <div className="toast error">{error}</div> : null}
      {message ? <div className="toast success">{message}</div> : null}

      <form className="panel stack" onSubmit={onSubmit}>
        <div className="grid-2">
          <div className="field">
            <label htmlFor="offering">Course offering</label>
            <select id="offering" value={offeringId} onChange={(e) => setOfferingId(e.target.value)}>
              {offerings.map((o) => (
                <option key={o.offering_id} value={o.offering_id}>
                  {o.sub_code} · {o.sub_name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="date">Session date</label>
            <input
              id="date"
              type="date"
              value={sessionDate}
              onChange={(e) => setSessionDate(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="field">
          <label htmlFor="topic">Topic (optional)</label>
          <input
            id="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder={selected ? `${selected.sub_code} lecture` : 'Lecture topic'}
          />
        </div>

        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Enroll</th>
                <th>Student</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {roster.map((s) => (
                <tr key={s.std_id}>
                  <td>{s.enroll_no}</td>
                  <td>{s.name}</td>
                  <td>
                    <select
                      value={statusMap[s.std_id] || 'present'}
                      onChange={(e) =>
                        setStatusMap((prev) => ({ ...prev, [s.std_id]: e.target.value }))
                      }
                    >
                      {STATUSES.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
              {!roster.length ? (
                <tr>
                  <td colSpan={3} className="empty">
                    No students on this roster.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>

        <button className="btn btn-primary" type="submit" disabled={saving || !roster.length}>
          {saving ? 'Saving…' : 'Save attendance session'}
        </button>
      </form>

      <section className="panel" style={{ marginTop: 18 }}>
        <h3 style={{ marginTop: 0 }}>Recent sessions</h3>
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Date</th>
                <th>Topic</th>
                <th>Present</th>
                <th>Absent</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => {
                const present = session.records.filter((r) =>
                  ['present', 'late', 'excused'].includes(r.status),
                ).length
                const absent = session.records.filter((r) => r.status === 'absent').length
                return (
                  <tr key={session.session_id}>
                    <td>{session.session_date}</td>
                    <td>{session.topic || '—'}</td>
                    <td>{present}</td>
                    <td>{absent}</td>
                  </tr>
                )
              })}
              {!sessions.length ? (
                <tr>
                  <td colSpan={4} className="empty">
                    No sessions recorded for this course yet.
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
