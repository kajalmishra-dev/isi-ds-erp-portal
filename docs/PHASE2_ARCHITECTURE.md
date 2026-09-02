# Phase 2 — Architecture lock

Smart Student ERP target for the next build sprints. Current product is a marks/exams MVP; this document locks roles, data model, and API surface before Phase 3 coding.

## Product slice (in scope)

| Keep / ship | Add next | Defer |
|-------------|----------|--------|
| Auth (JWT), admin, student | Faculty role + profile | Fees, hostel, library |
| Students, exams, subjects, marks | Attendance | SSO / payments |
| Official PDF marksheet | Assignments + submissions | Multi-tenant campuses |
| Forgot / reset password | Notices + in-app notifications | Full LMS |
| React (`web/`) + FastAPI | Dashboards / analytics | Mobile apps |
| | Grounded AI assistant (after real data) | |

Legacy Streamlit under `frontend/` stays unused by Compose; archive or delete after Phase 3 UI is solid.

## Roles

| Role | Who | Primary jobs |
|------|-----|----------------|
| `admin` | Registrar / academic office | Users, departments, programs, exams, subjects, marks oversight, notices, reports |
| `faculty` | Course instructors | Own courses, attendance, assignments, grade entry for own subjects |
| `student` | Enrolled learners | Dashboard, timetable/notices, attendance %, submit work, marksheet/PDF |

`users.designation` today is `admin | student`. Extend to `admin | faculty | student` (string enum; migrate existing rows unchanged).

### Permission matrix (high level)

| Capability | admin | faculty | student |
|------------|:-----:|:-------:|:-------:|
| Manage all students / exams / subjects | ✓ | | |
| Manage faculty accounts | ✓ | | |
| Mark attendance (own courses) | ✓ | ✓ | |
| View own attendance | | | ✓ |
| Create assignments (own courses) | ✓ | ✓ | |
| Submit assignment | | | ✓ |
| Upsert marks (scoped) | ✓ | ✓ (own subjects) | |
| Publish notices | ✓ | ✓ (course) | |
| Download marksheet PDF | | | ✓ |
| Analytics (aggregate) | ✓ | ✓ (own courses) | own only |
| AI Q&A over own academic data | ✓ | ✓ | ✓ |

## Target ERD (logical)

```
users
  user_id PK, username, password, designation, is_active, timestamps

admins          (1:1 users) — profile fields
faculty         (1:1 users) — employee_code, dept_id, name, email, phone
students        (1:1 users) — enrollment_no, program_id, semester, section, …

departments     — dept_id, code, name
programs        — program_id, dept_id, name, duration_semesters
courses         — course_id, program_id, code, title, credits, semester_no
  (maps today’s subjects → courses; keep subject_id alias during migration)

course_offerings — offering_id, course_id, academic_year, semester_term, faculty_id
enrollments      — student_id, offering_id, status

exams            — existing
marks            — existing; add offering_id / faculty_id when grading scoped

attendance_sessions — session_id, offering_id, session_date, topic, taken_by
attendance_records  — session_id, student_id, status (present|absent|late|excused)

assignments      — assignment_id, offering_id, title, due_at, max_score, created_by
submissions      — assignment_id, student_id, submitted_at, file_url/text, score, feedback

notices          — notice_id, title, body, audience (all|role|offering), created_by, published_at
notifications    — user_id, notice_id/ref, read_at

audit_logs       — actor_id, action, entity, entity_id, at, meta JSON
```

### Migration stance

- Short term: `create_all` + additive columns/tables; seed extends with faculty demo users.
- Next: introduce Alembic; stop relying on `SEED_RESET` for day-to-day boots (`SEED_RESET=false` by default).

## API map (Phase 3+)

Prefix remains `/api`. Auth: Bearer JWT; role checks in dependencies.

### Auth (existing + small extensions)
- `POST /api/auth/login`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`
- `GET  /api/auth/me` *(add)* — current user + role profile

### Admin (existing + extensions)
- Existing: `/api/admin/dashboard`, students, exams, subjects, marks CRUD
- Add: faculty CRUD, departments/programs (minimal), notices publish, analytics summary

### Faculty *(new router `/api/faculty`)*
- `GET  /dashboard`
- `GET  /offerings` — my courses
- `POST /offerings/{id}/attendance/sessions`
- `POST /offerings/{id}/attendance/sessions/{sid}/records`
- `GET  /offerings/{id}/attendance`
- `POST /offerings/{id}/assignments`
- `GET  /offerings/{id}/assignments`
- `PATCH /assignments/{id}/submissions/{sid}` — score/feedback
- `POST /offerings/{id}/marks` — scoped grade entry

### Student (existing + extensions)
- Existing: exams, marksheet, marksheet PDF
- Add: `GET /dashboard`, `GET /attendance`, `GET /assignments`, `POST /assignments/{id}/submit`, `GET /notices`

### Shared
- `GET /api/notices` (role-filtered)
- `GET /api/notifications`
- `POST /api/ai/ask` *(later)* — answers only from caller-scoped DB facts; no free-form invention

## Build order (Phase 3)

1. ~~Stabilize runtime (Compose healthy, `SEED_RESET=false`, demo seed once).~~
2. ~~Faculty model + login + shell UI.~~
3. ~~Course offerings + attendance (faculty take / student view %).~~
4. ~~Assignments + submissions.~~
5. ~~Notices + richer dashboards.~~
6. ~~Analytics widgets from real aggregates.~~
7. ~~Grounded AI assistant.~~

Phase 2+3 flagship slice complete for the deep MVP.

## Demo accounts (target after Phase 3 seed)

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Faculty | `faculty` | `faculty123` |
| Student | `student` | `student123` |

## Non-goals for Phase 2

No major feature coding in this phase beyond stabilize defaults and this lock document.
`frontend/` Streamlit is not in the product path.
