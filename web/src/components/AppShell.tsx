import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../lib/auth'

const adminLinks = [
  { to: '/admin', label: 'Registrar desk', end: true },
  { to: '/admin/analytics', label: 'Analytics' },
  { to: '/admin/assistant', label: 'Assistant' },
  { to: '/admin/students', label: 'Student roster' },
  { to: '/admin/exams', label: 'Examinations' },
  { to: '/admin/subjects', label: 'Subjects' },
  { to: '/admin/marks', label: 'Post marks' },
  { to: '/admin/notices', label: 'Notices' },
]

const facultyLinks = [
  { to: '/faculty', label: 'Faculty desk', end: true },
  { to: '/faculty/analytics', label: 'Analytics' },
  { to: '/faculty/assistant', label: 'Assistant' },
  { to: '/faculty/attendance', label: 'Attendance' },
  { to: '/faculty/assignments', label: 'Assignments' },
  { to: '/faculty/notices', label: 'Notices' },
]

const studentLinks = [
  { to: '/student', label: 'Student desk', end: true },
  { to: '/student/analytics', label: 'My analytics' },
  { to: '/student/assistant', label: 'Assistant' },
  { to: '/student/assignments', label: 'Assignments' },
  { to: '/student/marksheet', label: 'My marksheet' },
  { to: '/student/notices', label: 'Notices' },
]

function workspaceLabel(role: string | null) {
  if (role === 'admin') return 'Registrar workspace'
  if (role === 'faculty') return 'Faculty workspace'
  return 'Student workspace'
}

export function AppShell({
  title,
  subtitle,
  children,
}: {
  title: string
  subtitle: string
  children: ReactNode
}) {
  const { role, username, logout } = useAuth()
  const links = role === 'admin' ? adminLinks : role === 'faculty' ? facultyLinks : studentLinks

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">
          <strong>Meridian ERP</strong>
          <span>{workspaceLabel(role)}</span>
        </div>
        <nav className="nav-list">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div style={{ marginTop: 'auto' }}>
          <div style={{ color: 'var(--muted)', marginBottom: 10, fontSize: '0.92rem' }}>
            Signed in as <strong style={{ color: 'var(--ink)' }}>{username}</strong>
          </div>
          <button className="btn btn-ghost" type="button" onClick={logout}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="main">
        <div className="topbar">
          <div className="page-title">
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
        </div>
        {children}
      </main>
    </div>
  )
}
