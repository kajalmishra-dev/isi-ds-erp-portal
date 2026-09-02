import type { ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'

export function PublicLayout({ children }: { children?: ReactNode }) {
  return (
    <div className="public-site">
      <header className="site-header">
        <Link to="/" className="site-brand">
          <span className="crest">MIC</span>
          <div>
            <strong>Meridian Campus ERP</strong>
            <small>B.Tech CS & AI · Academic Portal</small>
          </div>
        </Link>
        <nav className="site-nav">
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/academics">Academics</NavLink>
          <NavLink to="/login">Sign in</NavLink>
          <NavLink to="/forgot-password">Forgot password</NavLink>
        </nav>
      </header>
      {children}
      <footer className="site-footer">
        <div>
          <strong>Academic Records Office</strong>
          <p>Meridian Institute of Computing · Demo academic ERP</p>
        </div>
        <div>
          <p>Helpdesk: records@meridian.edu</p>
          <p>Mon–Fri · 09:30–17:30 IST</p>
        </div>
      </footer>
    </div>
  )
}
