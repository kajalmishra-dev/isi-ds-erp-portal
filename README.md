# Meridian Campus ERP

Full-stack academic ERP demo for a fictional campus. Built to show end-to-end product work: auth, roles, seeded data, and a UI people can actually click through.

Not affiliated with any real college.

**Live demo:** [isi-ds-erp-portal.vercel.app](https://isi-ds-erp-portal.vercel.app)

---

## Overview

| Layer | Stack |
|-------|--------|
| Web | React, Vite, TypeScript |
| API | FastAPI, SQLAlchemy, JWT |
| Data | PostgreSQL |

**Roles**

- **Admin** - roster, subjects, exams, marks, notices
- **Faculty** - attendance, assignments, grading
- **Student** - dashboard, marksheet, submissions, grounded academic assistant

**Demo sandboxes** - each visitor gets a private copy of the seed world. Changes stay in that sandbox; new visitors still see clean original data.

---

## Try it

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Faculty | `faculty` | `faculty123` |
| Student | `student` | `student123` |

The API is on Render free tier. After idle time the first request can take ~30-60s while the service wakes. Opening `/health` on the API once before login helps.

---

## Quick start

### Docker

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| App | http://localhost:8501 |
| API docs | http://localhost:8000/docs |

### Local (API + Vite)

```bash
# API
cd backend
py -3.12 -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

```bash
# Web
cd web
npm install
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`.

---

## Repo map

```
backend/     FastAPI app, models, services, seed, tenant sandboxes
web/         React UI (Vercel root)
docs/        Architecture notes
render.yaml  Render API + Postgres blueprint
```

---

## Deploy

| Piece | Host | Notes |
|-------|------|--------|
| Frontend | Vercel | Root directory `web` |
| API + DB | Render | Blueprint from `render.yaml` |
| API URL | Env | `VITE_API_BASE_URL` (see `web/.env.production`) |
| CORS | Render env | `CORS_ORIGINS` must include the Vercel origin |

---

## Optional

Set `OPENAI_API_KEY` on the API for LLM polish on the assistant. Without it, answers stay grounded in DB facts only.

More detail: [docs/PHASE2_ARCHITECTURE.md](docs/PHASE2_ARCHITECTURE.md)

---

Portfolio / learning project. Issues and feedback welcome.
