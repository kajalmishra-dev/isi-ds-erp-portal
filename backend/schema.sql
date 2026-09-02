-- #backend>schema.sql

-- ERP Portal Database Schema (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users (central auth table)
CREATE TABLE users (
    user_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username    VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,           -- bcrypt hash
    designation VARCHAR(20) NOT NULL              -- 'admin' | 'faculty' | 'student'
                CHECK (designation IN ('admin','faculty','student')),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_designation ON users(designation);

-- Admins
CREATE TABLE admins (
    adm_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    phone       VARCHAR(20),
    email       VARCHAR(100) UNIQUE NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Students
CREATE TABLE students (
    std_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    enroll_no   VARCHAR(30) UNIQUE NOT NULL,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    phone       VARCHAR(20),
    email       VARCHAR(100) UNIQUE NOT NULL,
    semester    SMALLINT NOT NULL CHECK (semester BETWEEN 1 AND 12),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_students_enroll ON students(enroll_no);
CREATE INDEX idx_students_semester ON students(semester);

-- Exams
CREATE TABLE exams (
    exam_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_name   VARCHAR(100) NOT NULL,
    year        SMALLINT NOT NULL,
    semester    SMALLINT CHECK (semester BETWEEN 1 AND 12),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (exam_name, year, semester)
);
CREATE INDEX idx_exams_year ON exams(year);

-- Subjects
CREATE TABLE subjects (
    sub_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sub_code    VARCHAR(20) UNIQUE NOT NULL,
    sub_name    VARCHAR(100) NOT NULL,
    max_marks   SMALLINT NOT NULL DEFAULT 100,
    semester    SMALLINT CHECK (semester BETWEEN 1 AND 12),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_subjects_semester ON subjects(semester);

-- Marks  (1 row = 1 student x 1 subject x 1 exam)
CREATE TABLE marks (
    mark_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    std_id        UUID NOT NULL REFERENCES students(std_id) ON DELETE CASCADE,
    exam_id       UUID NOT NULL REFERENCES exams(exam_id) ON DELETE CASCADE,
    sub_id        UUID NOT NULL REFERENCES subjects(sub_id) ON DELETE CASCADE,
    marks_obtained SMALLINT NOT NULL CHECK (marks_obtained >= 0),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (std_id, exam_id, sub_id)   -- one row per combo
);
CREATE INDEX idx_marks_student ON marks(std_id);
CREATE INDEX idx_marks_exam    ON marks(exam_id);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

-- Password reset (campus portal)
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    code_hash   VARCHAR(255) NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    used        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_reset_user ON password_reset_tokens(user_id);

-- Faculty
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    employee_code VARCHAR(30) UNIQUE NOT NULL,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    phone         VARCHAR(20),
    email         VARCHAR(100) UNIQUE NOT NULL,
    department    VARCHAR(100) NOT NULL DEFAULT 'Data Science',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Course offerings (faculty teaches a subject in a term)
CREATE TABLE IF NOT EXISTS course_offerings (
    offering_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sub_id        UUID NOT NULL REFERENCES subjects(sub_id) ON DELETE CASCADE,
    faculty_id    UUID NOT NULL REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    academic_year SMALLINT NOT NULL,
    term          VARCHAR(20) NOT NULL DEFAULT 'Odd',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sub_id, academic_year, term)
);

CREATE TABLE IF NOT EXISTS attendance_sessions (
    session_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    offering_id   UUID NOT NULL REFERENCES course_offerings(offering_id) ON DELETE CASCADE,
    session_date  DATE NOT NULL,
    topic         VARCHAR(200),
    taken_by      UUID REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_att_session_offering ON attendance_sessions(offering_id);

CREATE TABLE IF NOT EXISTS attendance_records (
    record_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id    UUID NOT NULL REFERENCES attendance_sessions(session_id) ON DELETE CASCADE,
    std_id        UUID NOT NULL REFERENCES students(std_id) ON DELETE CASCADE,
    status        VARCHAR(20) NOT NULL DEFAULT 'present'
                  CHECK (status IN ('present','absent','late','excused')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (session_id, std_id)
);
CREATE INDEX IF NOT EXISTS idx_att_record_session ON attendance_records(session_id);
CREATE INDEX IF NOT EXISTS idx_att_record_student ON attendance_records(std_id);

CREATE TABLE IF NOT EXISTS assignments (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    offering_id   UUID NOT NULL REFERENCES course_offerings(offering_id) ON DELETE CASCADE,
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    due_at        TIMESTAMPTZ NOT NULL,
    max_score     DOUBLE PRECISION NOT NULL DEFAULT 100,
    created_by    UUID REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_assignments_offering ON assignments(offering_id);

CREATE TABLE IF NOT EXISTS submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assignment_id UUID NOT NULL REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    std_id        UUID NOT NULL REFERENCES students(std_id) ON DELETE CASCADE,
    content       TEXT NOT NULL,
    submitted_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    score         DOUBLE PRECISION,
    feedback      TEXT,
    graded_at     TIMESTAMPTZ,
    graded_by     UUID REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    UNIQUE (assignment_id, std_id)
);
CREATE INDEX IF NOT EXISTS idx_submissions_assignment ON submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_submissions_student ON submissions(std_id);

CREATE TABLE IF NOT EXISTS notices (
    notice_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title        VARCHAR(200) NOT NULL,
    body         TEXT NOT NULL,
    audience     VARCHAR(20) NOT NULL DEFAULT 'all'
                 CHECK (audience IN ('all','admin','faculty','student','offering')),
    offering_id  UUID REFERENCES course_offerings(offering_id) ON DELETE CASCADE,
    created_by   UUID REFERENCES users(user_id) ON DELETE SET NULL,
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    published_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notices_audience ON notices(audience);
CREATE INDEX IF NOT EXISTS idx_notices_offering ON notices(offering_id);

CREATE TABLE IF NOT EXISTS notice_reads (
    read_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notice_id UUID NOT NULL REFERENCES notices(notice_id) ON DELETE CASCADE,
    user_id   UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    read_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (notice_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_notice_reads_user ON notice_reads(user_id);
