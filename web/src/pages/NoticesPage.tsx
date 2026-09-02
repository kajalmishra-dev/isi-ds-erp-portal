import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { AppShell } from '../components/AppShell'
import { ApiError, api } from '../lib/api'
import { useAuth } from '../lib/auth'

type Notice = {
  notice_id: string
  title: string
  body: string
  audience: string
  offering_id: string | null
  offering_label: string | null
  author_name: string | null
  author_role: string | null
  published_at: string
  is_read: boolean
}

type Offering = {
  offering_id: string
  sub_code: string
  sub_name: string
}

type NoticesPageProps = {
  canPublish: boolean
  publishPath: '/api/admin/notices' | '/api/faculty/notices'
  title?: string
}

export function NoticesPage({
  canPublish,
  publishPath,
  title = 'Notices',
}: NoticesPageProps) {
  const { token, logout, role } = useAuth()
  const [notices, setNotices] = useState<Notice[]>([])
  const [unread, setUnread] = useState(0)
  const [offerings, setOfferings] = useState<Offering[]>([])
  const [noticeTitle, setNoticeTitle] = useState('')
  const [body, setBody] = useState('')
  const [audience, setAudience] = useState(role === 'faculty' ? 'student' : 'all')
  const [offeringId, setOfferingId] = useState('')
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

  function reload(currentToken: string) {
    return api
      .get<{ notices: Notice[]; unread_count: number }>('/api/notices', currentToken)
      .then((data) => {
        setNotices(data.notices)
        setUnread(data.unread_count)
      })
  }

  useEffect(() => {
    if (!token) return
    reload(token).catch((err) => {
      if (handleAuth(err)) return
      setError(err instanceof Error ? err.message : 'Failed to load notices')
    })
    if (canPublish && role === 'faculty') {
      api
        .get<Offering[]>('/api/faculty/offerings', token)
        .then((list) => {
          setOfferings(list)
          if (list[0]) setOfferingId(list[0].offering_id)
        })
        .catch(() => {
          /* optional */
        })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, canPublish, role])

  async function onPublish(event: FormEvent) {
    event.preventDefault()
    if (!token) return
    setSaving(true)
    setError('')
    setMessage('')
    try {
      await api.post(publishPath, token, {
        title: noticeTitle.trim(),
        body: body.trim(),
        audience,
        offering_id: audience === 'offering' ? offeringId : null,
      })
      setNoticeTitle('')
      setBody('')
      setMessage('Notice published.')
      await reload(token)
    } catch (err) {
      if (handleAuth(err)) return
      setError(err instanceof Error ? err.message : 'Could not publish notice')
    } finally {
      setSaving(false)
    }
  }

  async function markRead(noticeId: string) {
    if (!token) return
    try {
      await api.post(`/api/notices/${noticeId}/read`, token, {})
      setNotices((prev) =>
        prev.map((n) => (n.notice_id === noticeId ? { ...n, is_read: true } : n)),
      )
      setUnread((count) => Math.max(0, count - 1))
    } catch (err) {
      if (handleAuth(err)) return
    }
  }

  const audienceOptions =
    role === 'faculty'
      ? [
          { value: 'all', label: 'Everyone' },
          { value: 'student', label: 'Students' },
          { value: 'faculty', label: 'Faculty' },
          { value: 'offering', label: 'One course' },
        ]
      : [
          { value: 'all', label: 'Everyone' },
          { value: 'student', label: 'Students' },
          { value: 'faculty', label: 'Faculty' },
          { value: 'admin', label: 'Admins' },
          { value: 'offering', label: 'One course' },
        ]

  return (
    <AppShell
      title={title}
      subtitle={
        unread
          ? `${unread} unread notice${unread === 1 ? '' : 's'} in your feed.`
          : 'Campus and course announcements for your role.'
      }
    >
      {error ? <div className="toast error">{error}</div> : null}
      {message ? <div className="toast success">{message}</div> : null}

      {canPublish ? (
        <form className="panel stack" onSubmit={onPublish}>
          <h3 style={{ margin: 0 }}>Publish notice</h3>
          <div className="grid-2">
            <div className="field">
              <label htmlFor="ntitle">Title</label>
              <input
                id="ntitle"
                value={noticeTitle}
                onChange={(e) => setNoticeTitle(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="audience">Audience</label>
              <select id="audience" value={audience} onChange={(e) => setAudience(e.target.value)}>
                {audienceOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {audience === 'offering' ? (
            <div className="field">
              <label htmlFor="course">Course</label>
              {role === 'faculty' ? (
                <select
                  id="course"
                  value={offeringId}
                  onChange={(e) => setOfferingId(e.target.value)}
                  required
                >
                  {offerings.map((o) => (
                    <option key={o.offering_id} value={o.offering_id}>
                      {o.sub_code} · {o.sub_name}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  id="course"
                  value={offeringId}
                  onChange={(e) => setOfferingId(e.target.value)}
                  placeholder="Course offering UUID"
                  required
                />
              )}
            </div>
          ) : null}
          <div className="field">
            <label htmlFor="body">Message</label>
            <textarea
              id="body"
              rows={4}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? 'Publishing…' : 'Publish'}
          </button>
        </form>
      ) : null}

      <section className="panel" style={{ marginTop: canPublish ? 18 : 0 }}>
        <h3 style={{ marginTop: 0 }}>Your feed</h3>
        <div className="stack" style={{ gap: 14 }}>
          {notices.map((notice) => (
            <article
              key={notice.notice_id}
              style={{
                borderTop: '1px solid var(--line)',
                paddingTop: 14,
                opacity: notice.is_read ? 0.85 : 1,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                <div>
                  <strong style={{ fontFamily: 'var(--display)', fontSize: '1.15rem' }}>
                    {notice.title}
                  </strong>
                  <div style={{ color: 'var(--muted)', fontSize: '0.88rem', marginTop: 4 }}>
                    {notice.author_name || 'Campus office'}
                    {notice.author_role ? ` · ${notice.author_role}` : ''}
                    {' · '}
                    {new Date(notice.published_at).toLocaleString()}
                    {' · '}
                    {notice.offering_label || notice.audience}
                    {!notice.is_read ? ' · unread' : ''}
                  </div>
                </div>
                {!notice.is_read ? (
                  <button
                    className="btn btn-ghost btn-tiny"
                    type="button"
                    onClick={() => markRead(notice.notice_id)}
                  >
                    Mark read
                  </button>
                ) : null}
              </div>
              <p style={{ marginBottom: 0, whiteSpace: 'pre-wrap' }}>{notice.body}</p>
            </article>
          ))}
          {!notices.length ? <div className="empty">No notices in your feed yet.</div> : null}
        </div>
      </section>
    </AppShell>
  )
}
