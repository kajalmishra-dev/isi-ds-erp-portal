import { PublicLayout } from '../components/PublicLayout'

const CATALOGUE: [string, string, string][] = [
  ['CSAI101', 'Python Programming', '1'],
  ['CSAI102', 'Mathematics for Computer Science', '1'],
  ['CSAI103', 'Web Fundamentals (HTML, CSS, JS)', '1'],
  ['CSAI104', 'Data Structures & Algorithms I', '1'],
  ['CSAI105', 'UI/UX Essentials', '1'],
  ['CSAI201', 'Data Structures & Algorithms II', '2'],
  ['CSAI202', 'React & Frontend Engineering', '2'],
  ['CSAI203', 'Databases (SQL & MongoDB)', '2'],
  ['CSAI204', 'Introduction to AI & ML', '2'],
  ['CSAI205', 'OOP & Advanced Programming', '2'],
  ['CSAI301', 'Backend Engineering with Node.js', '3'],
  ['CSAI302', 'Machine Learning', '3'],
  ['CSAI303', 'Data & Visual Analytics', '3'],
  ['CSAI304', 'System Design Foundations', '3'],
  ['CSAI305', 'Mathematics for Artificial Intelligence', '3'],
  ['CSAI401', 'Operating Systems', '4'],
  ['CSAI402', 'Natural Language Processing', '4'],
  ['CSAI403', 'Computer Vision', '4'],
  ['CSAI404', 'Capstone Project Studio', '4'],
]

export function AcademicsPage() {
  return (
    <PublicLayout>
      <main className="public-main" style={{ width: 'min(860px, calc(100% - 40px))' }}>
        <section className="panel stack">
          <div>
            <p className="eyebrow">Subject list</p>
            <h1 style={{ margin: 0, fontFamily: 'var(--font)', fontWeight: 700, fontSize: '1.85rem' }}>
              What students study
            </h1>
            <p style={{ color: 'var(--muted)' }}>
              Demo B.Tech CS & AI subjects by semester. Sign in to use attendance, assignments, and
              marks.
            </p>
          </div>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Course</th>
                  <th>Semester</th>
                </tr>
              </thead>
              <tbody>
                {CATALOGUE.map(([code, name, sem]) => (
                  <tr key={code}>
                    <td>{code}</td>
                    <td>{name}</td>
                    <td>{sem}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </PublicLayout>
  )
}
