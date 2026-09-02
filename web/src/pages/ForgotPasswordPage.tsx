import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { PublicLayout } from '../components/PublicLayout'
import { api } from '../lib/api'

type Step = 'verify' | 'reset' | 'done'

export function ForgotPasswordPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState<Step>('verify')
  const [role, setRole] = useState<'student' | 'staff'>('student')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [enrollNo, setEnrollNo] = useState('')
  const [resetCode, setResetCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function requestCode(event: FormEvent) {
    event.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)
    try {
      const res = await api.postPublic<{
        message: string
        reset_code: string | null
      }>('/api/auth/forgot-password', {
        username: username.trim(),
        email: email.trim(),
        enroll_no: role === 'student' ? enrollNo.trim() : null,
      })
      setMessage(res.message)
      if (res.reset_code) {
        setResetCode(res.reset_code)
        setStep('reset')
      } else {
        setError('Details did not match academic records.')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not start reset')
    } finally {
      setLoading(false)
    }
  }

  async function submitReset(event: FormEvent) {
    event.preventDefault()
    setError('')
    if (newPassword !== confirm) {
      setError('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      const res = await api.postPublic<{ message: string }>('/api/auth/reset-password', {
        username: username.trim(),
        reset_code: resetCode.trim(),
        new_password: newPassword,
      })
      setMessage(res.message)
      setStep('done')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Reset failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PublicLayout>
      <main className="public-main narrow">
        <section className="panel stack auth-card">
          <div>
            <h1>Forgot password</h1>
            <p className="lede">
              Verify campus identity. In production the code is emailed; here it appears after a
              successful match.
            </p>
          </div>

          {step === 'verify' ? (
            <form className="stack" onSubmit={requestCode}>
              <div className="role-tabs">
                <button
                  type="button"
                  className={`role-tab${role === 'student' ? ' active' : ''}`}
                  onClick={() => setRole('student')}
                >
                  <strong>Student</strong>
                  <span>Enroll + email</span>
                </button>
                <button
                  type="button"
                  className={`role-tab${role === 'staff' ? ' active' : ''}`}
                  onClick={() => setRole('staff')}
                >
                  <strong>Staff</strong>
                  <span>Office email</span>
                </button>
              </div>
              <div className="field">
                <label htmlFor="username">Username</label>
                <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
              </div>
              {role === 'student' ? (
                <div className="field">
                  <label htmlFor="enroll">Enroll number</label>
                  <input
                    id="enroll"
                    value={enrollNo}
                    onChange={(e) => setEnrollNo(e.target.value)}
                    placeholder="DS2026-DEMO"
                    required
                  />
                </div>
              ) : null}
              <div className="field">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={
                    role === 'student'
                      ? 'aarav.mehta@student.meridian.edu'
                      : 'registrar@meridian.edu'
                  }
                  required
                />
              </div>
              {error ? <div className="toast error">{error}</div> : null}
              <button className="btn btn-primary" type="submit" disabled={loading}>
                {loading ? 'Checking…' : 'Get reset code'}
              </button>
            </form>
          ) : null}

          {step === 'reset' ? (
            <form className="stack" onSubmit={submitReset}>
              <div className="toast success">
                Code for <strong>{username}</strong>: <code>{resetCode}</code>
              </div>
              <div className="field">
                <label htmlFor="code">Reset code</label>
                <input id="code" value={resetCode} onChange={(e) => setResetCode(e.target.value)} required />
              </div>
              <div className="field">
                <label htmlFor="np">New password</label>
                <input
                  id="np"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  minLength={6}
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="cp">Confirm password</label>
                <input
                  id="cp"
                  type="password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  minLength={6}
                  required
                />
              </div>
              {error ? <div className="toast error">{error}</div> : null}
              <button className="btn btn-primary" type="submit" disabled={loading}>
                {loading ? 'Updating…' : 'Update password'}
              </button>
            </form>
          ) : null}

          {step === 'done' ? (
            <div className="stack">
              <div className="toast success">{message}</div>
              <button className="btn btn-primary" type="button" onClick={() => navigate('/login')}>
                Go to sign in
              </button>
            </div>
          ) : null}

          <Link to="/login" style={{ color: 'var(--brand)', fontWeight: 600 }}>
            Back to sign in
          </Link>
        </section>
      </main>
    </PublicLayout>
  )
}
