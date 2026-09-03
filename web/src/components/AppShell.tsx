import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../lib/auth'

const adminLinks = [
  { to: '/admin', label: 'Overview', hint: 'Counts & recent marks', end: true },
  { to: '/admin/students', label: 'Students', hint: 'Add / edit roster' },
  { to: '/admin/exams', label: 'Exams', hint: 'Create exam sessions' },
  { to: '/admin/subjects', label: 'Subjects', hint: 'Course catalogue' },
  { to: '/admin/marks', label: 'Marks', hint: 'Enter student scores' },
  { to: '/admin/notices', label: 'Notices', hint: 'Campus announcements' },
  { to: '/admin/analytics', label: 'Analytics', hint: 'Charts & trends' },
  { to: '/admin/assistant', label: 'Ask AI', hint: 'Questions from your data' },
]

const facultyLinks = [
  { to: '/faculty', label: 'Overview', hint: 'Your courses', end: true },
  { to: '/faculty/attendance', label: 'Attendance', hint: 'Mark present / absent' },
  { to: '/faculty/assignments', label: 'Assignments', hint: 'Publish & grade work' },
  { to: '/faculty/notices', label: 'Notices', hint: 'Class announcements' },
  { to: '/faculty/analytics', label: 'Analytics', hint: 'Course insights' },
  { to: '/faculty/assistant', label: 'Ask AI', hint: 'Questions from your data' },
]

const studentLinks = [
  { to: '/student', label: 'Overview', hint: 'Semester snapshot', end: true },
  { to: '/student/assignments', label: 'Assignments', hint: 'Submit your work' },
  { to: '/student/marksheet', label: 'Marksheet', hint: 'View & download PDF' },
  { to: '/student/notices', label: 'Notices', hint: 'Campus updates' },
  { to: '/student/analytics', label: 'My analytics', hint: 'Attendance & scores' },
  { to: '/student/assistant', label: 'Ask AI', hint: 'Questions from your data' },
]

function roleMeta(role: string | null) {
  if (role === 'admin') return { title: 'Admin', badge: 'Registrar', workspace: 'Manage students, exams & marks' }
  if (role === 'faculty') return { title: 'Faculty', badge: 'Teacher', workspace: 'Attendance, assignments & grading' }
  return { title: 'Student', badge: 'Learner', workspace: 'Attendance, assignments & marksheet' }
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
  const meta = roleMeta(role)

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">
          <strong>Campus ERP</strong>
          <span>{meta.workspace}</span>
          <span className={`role-pill role-${role ?? 'student'}`}>{meta.badge}</span>
        </div>
        <nav className="nav-list" aria-label="Main menu">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              title={link.hint}
            >
              <span className="nav-label">{link.label}</span>
              <span className="nav-hint">{link.hint}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <div className="signed-as">
            <span>Signed in as</span>
            <strong>{username}</strong>
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
