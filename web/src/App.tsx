import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { useAuth } from './lib/auth'
import { AssistantPage } from './pages/AssistantPage'
import { AcademicsPage } from './pages/AcademicsPage'
import { ForgotPasswordPage } from './pages/ForgotPasswordPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { NoticesPage } from './pages/NoticesPage'
import { AdminAnalyticsPage } from './pages/admin/AnalyticsPage'
import { AdminDashboardPage } from './pages/admin/DashboardPage'
import { ExamsPage } from './pages/admin/ExamsPage'
import { MarksPage } from './pages/admin/MarksPage'
import { StudentsPage } from './pages/admin/StudentsPage'
import { SubjectsPage } from './pages/admin/SubjectsPage'
import { FacultyAnalyticsPage } from './pages/faculty/AnalyticsPage'
import { FacultyAttendancePage } from './pages/faculty/AttendancePage'
import { FacultyAssignmentsPage } from './pages/faculty/AssignmentsPage'
import { FacultyDashboardPage } from './pages/faculty/DashboardPage'
import { StudentAnalyticsPage } from './pages/student/AnalyticsPage'
import { StudentAssignmentsPage } from './pages/student/AssignmentsPage'
import { StudentDashboardPage } from './pages/student/DashboardPage'
import { StudentMarksheetPage } from './pages/StudentMarksheetPage'

function homeForRole(role: string | null) {
  if (role === 'admin') return '/admin'
  if (role === 'faculty') return '/faculty'
  return '/student'
}

function RequireAuth({ role }: { role?: 'admin' | 'faculty' | 'student' }) {
  const auth = useAuth()
  if (!auth.token) return <Navigate to="/login" replace />
  if (role && auth.role !== role) {
    return <Navigate to={homeForRole(auth.role)} replace />
  }
  return <Outlet />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/academics" element={<AcademicsPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route element={<RequireAuth role="admin" />}>
        <Route path="/admin" element={<AdminDashboardPage />} />
        <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
        <Route path="/admin/students" element={<StudentsPage />} />
        <Route path="/admin/exams" element={<ExamsPage />} />
        <Route path="/admin/subjects" element={<SubjectsPage />} />
        <Route path="/admin/marks" element={<MarksPage />} />
        <Route path="/admin/assistant" element={<AssistantPage />} />
        <Route
          path="/admin/notices"
          element={<NoticesPage canPublish publishPath="/api/admin/notices" />}
        />
      </Route>
      <Route element={<RequireAuth role="faculty" />}>
        <Route path="/faculty" element={<FacultyDashboardPage />} />
        <Route path="/faculty/analytics" element={<FacultyAnalyticsPage />} />
        <Route path="/faculty/attendance" element={<FacultyAttendancePage />} />
        <Route path="/faculty/assignments" element={<FacultyAssignmentsPage />} />
        <Route path="/faculty/assistant" element={<AssistantPage />} />
        <Route
          path="/faculty/notices"
          element={<NoticesPage canPublish publishPath="/api/faculty/notices" />}
        />
      </Route>
      <Route element={<RequireAuth role="student" />}>
        <Route path="/student" element={<StudentDashboardPage />} />
        <Route path="/student/analytics" element={<StudentAnalyticsPage />} />
        <Route path="/student/assignments" element={<StudentAssignmentsPage />} />
        <Route path="/student/marksheet" element={<StudentMarksheetPage />} />
        <Route path="/student/assistant" element={<AssistantPage />} />
        <Route
          path="/student/notices"
          element={<NoticesPage canPublish={false} publishPath="/api/admin/notices" />}
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
