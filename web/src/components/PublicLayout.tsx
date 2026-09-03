import type { ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'

export function PublicLayout({
  children,
  tone = 'default',
}: {
  children?: ReactNode
  tone?: 'default' | 'home'
}) {
  return (
    <div className={`public-site${tone === 'home' ? ' public-site-home' : ''}`}>
      <header className="site-header">
        <Link to="/" className="site-brand">
          <span className="crest">ERP</span>
          <div>
            <strong>Campus Academic ERP</strong>
          </div>
        </Link>
        <nav className="site-nav">
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/academics">Subjects</NavLink>
          {tone !== 'home' ? (
            <NavLink
              to="/login"
              className={({ isActive }) => `nav-cta${isActive ? ' active' : ''}`}
            >
              Sign in
            </NavLink>
          ) : null}
        </nav>
      </header>
      {children}
      {tone !== 'home' ? (
        <footer className="site-footer site-footer-centered">
          <p className="home-tagline">
            Built for students, faculty, and admins -{' '}
            <Link to="/login">sign in</Link> to explore.
          </p>
        </footer>
      ) : null}
    </div>
  )
}
