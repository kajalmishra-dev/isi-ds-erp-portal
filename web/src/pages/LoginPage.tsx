import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { PublicLayout } from '../components/PublicLayout'
import { useAuth } from '../lib/auth'

export function LoginPage() {
  const { token, role, login, logout } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (token && role === 'admin') return <Navigate to="/admin" replace />
  if (token && role === 'faculty') return <Navigate to="/faculty" replace />
  if (token && role === 'student') return <Navigate to="/student" replace />

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setLoading(true)
    logout()
    try {
      const result = await login(username.trim(), password)
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
      <main className="public-main narrow">
        <form className="panel stack auth-card" onSubmit={onSubmit}>
          <div>
            <p className="eyebrow">Campus access</p>
            <h1>Welcome back</h1>
            <p className="lede">Sign in with your programme credentials.</p>
          </div>
          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              placeholder="admin or student"
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
            {loading ? 'Signing in…' : 'Enter portal'}
          </button>
          <div className="auth-links">
            <Link to="/forgot-password">Forgot password?</Link>
            <Link to="/">Campus home</Link>
          </div>
          <div className="demo-note">
            Registrar: <code>admin</code> / <code>admin123</code>
            <br />
            Faculty: <code>faculty</code> · <code>faculty2</code> · <code>faculty3</code> /{' '}
            <code>faculty123</code>
            <br />
            Student: <code>student</code> / <code>student123</code> (also <code>isha</code>,{' '}
            <code>vihaan</code>, …)
          </div>
        </form>
      </main>
    </PublicLayout>
  )
}
