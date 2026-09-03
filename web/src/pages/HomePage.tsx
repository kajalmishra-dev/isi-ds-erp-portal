import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { PublicLayout } from '../components/PublicLayout'
import type { Role } from '../lib/api'
import { useAuth } from '../lib/auth'

const QUICK_ROLES = [
  { id: 'admin' as Role, label: 'Admin', username: 'admin', password: 'admin123' },
  { id: 'faculty' as Role, label: 'Faculty', username: 'faculty', password: 'faculty123' },
  { id: 'student' as Role, label: 'Student', username: 'student', password: 'student123' },
]

function roleFromCredentials(username: string, password: string): Role | null {
  const match = QUICK_ROLES.find(
    (r) => r.username === username.trim().toLowerCase() && r.password === password,
  )
  return match?.id ?? null
}

export function HomePage() {
  const { token, role, loginDemo, logout } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [picked, setPicked] = useState<Role | ''>('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (token && role === 'admin') return <Navigate to="/admin" replace />
  if (token && role === 'faculty') return <Navigate to="/faculty" replace />
  if (token && role === 'student') return <Navigate to="/student" replace />

  function pickRole(account: (typeof QUICK_ROLES)[number]) {
    setPicked(account.id)
    setUsername(account.username)
    setPassword(account.password)
    setError('')
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setLoading(true)
    logout()
    try {
      const demoRole =
        picked || roleFromCredentials(username, password) || (username.trim().toLowerCase() as Role)
      if (!['admin', 'faculty', 'student'].includes(demoRole)) {
        throw new Error('Pick Admin, Faculty, or Student to open your private demo.')
      }
      const result = await loginDemo(demoRole)
      const dest =
        result.role === 'admin' ? '/admin' : result.role === 'faculty' ? '/faculty' : '/student'
      navigate(dest, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PublicLayout tone="home">
      <main className="home-page">
        <section className="campus-hero campus-hero-bleed">
          <div className="campus-hero-media" aria-hidden="true" />
          <div className="campus-hero-shade" aria-hidden="true" />

          <div className="hero-stage">
            <div className="campus-hero-inner">
              <p className="eyebrow">Campus Academic ERP</p>
              <h1>Your entire academic life, in one place.</h1>
              <p className="lede-lg">
                Attendance, assignments, grades, and schedules - one calm workspace for students,
                faculty, and admins.
              </p>
              <div className="hero-cta">
                <Link className="btn btn-ghost" to="/academics">
                  See subjects
                </Link>
              </div>
            </div>

            <form className="home-login" onSubmit={onSubmit}>
              <div className="home-login-head">
                <h2>Sign in</h2>
                <p>Each visitor gets a private copy of the demo data. Yours stays yours.</p>
              </div>

              <div className="home-role-row" role="group" aria-label="Quick role fill">
                {QUICK_ROLES.map((account) => (
                  <button
                    key={account.id}
                    type="button"
                    className={`home-role-chip${picked === account.id ? ' active' : ''}`}
                    onClick={() => pickRole(account)}
                  >
                    {account.label}
                  </button>
                ))}
              </div>

              <div className="field">
                <label htmlFor="home-username">Username</label>
                <input
                  id="home-username"
                  value={username}
                  onChange={(e) => {
                    setUsername(e.target.value)
                    setPicked('')
                  }}
                  autoComplete="username"
                  placeholder="Username"
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="home-password">Password</label>
                <input
                  id="home-password"
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    setPicked('')
                  }}
                  autoComplete="current-password"
                  placeholder="Password"
                  required
                />
              </div>

              {error ? <div className="toast error">{error}</div> : null}

              <button className="btn btn-primary home-login-submit" type="submit" disabled={loading}>
                {loading ? 'Opening your sandbox…' : 'Sign in'}
              </button>

              <div className="home-login-demos">
                <span>Demo access (same IDs in every private copy)</span>
                <p>
                  <code>admin</code> / <code>admin123</code>
                </p>
                <p>
                  <code>faculty</code> / <code>faculty123</code>
                </p>
                <p>
                  <code>student</code> / <code>student123</code>
                </p>
              </div>

              <p className="home-login-foot">
                <Link to="/forgot-password">Forgot password?</Link>
              </p>
            </form>
          </div>
        </section>
      </main>
    </PublicLayout>
  )
}
