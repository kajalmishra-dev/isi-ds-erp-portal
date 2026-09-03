import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { PublicLayout } from '../components/PublicLayout'
import type { Role } from '../lib/api'
import { useAuth } from '../lib/auth'

const DEMO_ACCOUNTS = [
  {
    id: 'admin' as Role,
    title: 'Admin',
    blurb: 'Students, exams, marks',
    username: 'admin',
    password: 'admin123',
  },
  {
    id: 'faculty' as Role,
    title: 'Faculty',
    blurb: 'Attendance & assignments',
    username: 'faculty',
    password: 'faculty123',
  },
  {
    id: 'student' as Role,
    title: 'Student',
    blurb: 'Marksheet & submissions',
    username: 'student',
    password: 'student123',
  },
]

export function LoginPage() {
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

  function pickDemo(account: (typeof DEMO_ACCOUNTS)[number]) {
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
        picked ||
        (DEMO_ACCOUNTS.find(
          (a) => a.username === username.trim().toLowerCase() && a.password === password,
        )?.id as Role | undefined)
      if (!demoRole) {
        throw new Error('Pick a demo role, or use the listed demo usernames and passwords.')
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
    <PublicLayout>
      <main className="public-main narrow login-wide">
        <form className="panel stack auth-card" onSubmit={onSubmit}>
          <div>
            <p className="eyebrow">Sign in</p>
            <h1>Enter the portal</h1>
            <p className="lede">
              Pick a demo role. You get a private copy of the original data - changes stay in your
              sandbox.
            </p>
          </div>

          <div className="role-tabs" role="group" aria-label="Demo accounts">
            {DEMO_ACCOUNTS.map((account) => (
              <button
                key={account.id}
                type="button"
                className={`role-tab${picked === account.id ? ' active' : ''}`}
                onClick={() => pickDemo(account)}
              >
                <strong>{account.title}</strong>
                <span>{account.blurb}</span>
              </button>
            ))}
          </div>

          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              placeholder="e.g. student"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>
          {error ? <div className="toast error">{error}</div> : null}
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Opening your sandbox…' : 'Sign in'}
          </button>
          <div className="auth-links">
            <Link to="/forgot-password">Forgot password?</Link>
            <Link to="/">Back to home</Link>
          </div>
          <div className="demo-note">
            <strong>Demo passwords</strong>
            <ul className="demo-list">
              <li>
                Admin → <code>admin</code> / <code>admin123</code>
              </li>
              <li>
                Faculty → <code>faculty</code> / <code>faculty123</code>
              </li>
              <li>
                Student → <code>student</code> / <code>student123</code>
              </li>
            </ul>
          </div>
        </form>
      </main>
    </PublicLayout>
  )
}
