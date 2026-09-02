import { Link } from 'react-router-dom'
import { PublicLayout } from '../components/PublicLayout'

export function HomePage() {
  return (
    <PublicLayout>
      <main className="public-main">
        <section className="campus-hero">
          <div className="campus-hero-copy">
            <p className="eyebrow">Campus Academic ERP</p>
            <h1>
              <span className="brand-line">Meridian Institute</span>
              Academic Portal
            </h1>
            <p className="lede-lg">
              Attendance, assignments, examinations, analytics, and official marksheets for a
              coding-first undergraduate programme — demo data only.
            </p>
            <div className="hero-cta">
              <Link className="btn btn-primary" to="/login">
                Sign in to portal
              </Link>
              <Link className="btn btn-ghost" to="/academics">
                View curriculum
              </Link>
            </div>
          </div>
        </section>

        <section className="feature-grid">
          <article className="panel">
            <div className="feature-icon">01</div>
            <h3>Students</h3>
            <p>Track attendance, submit labs, read notices, and download certified marksheets.</p>
          </article>
          <article className="panel">
            <div className="feature-icon">02</div>
            <h3>Faculty</h3>
            <p>Take attendance, publish coursework, grade submissions, and review course analytics.</p>
          </article>
          <article className="panel">
            <div className="feature-icon">03</div>
            <h3>Registrar</h3>
            <p>Manage roster, exams, subjects, marks, campus notices, and programme dashboards.</p>
          </article>
        </section>
      </main>
    </PublicLayout>
  )
}
