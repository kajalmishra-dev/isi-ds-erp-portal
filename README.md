# Meridian Campus ERP

A full-stack academic ERP I built to explore how a campus portal actually feels end-to-end — not just screens, but roles, data, and the quiet workflows people use every day.

This is a **demo product for a fictional institute**. It is not affiliated with any real college.

---

## What it does

Three roles share one system:

- **Admin** — students, subjects, exams, marks, notices  
- **Faculty** — attendance, assignments, coursework  
- **Student** — dashboard, marksheet, submissions, and a grounded academic assistant  

Under the hood: **React + Vite**, **FastAPI**, **PostgreSQL**, JWT auth.

On the public demo, each visitor gets a **private sandbox** — a fresh copy of the seed data. Your edits stay yours; the next person still sees the original world.

---

## Try the live demo

- **App:** [isi-ds-erp-portal.vercel.app](https://isi-ds-erp-portal.vercel.app)  
- **API health:** [meridian-erp-api.onrender.com/health](https://meridian-erp-api.onrender.com/health)

| Role    | Username  | Password     |
|---------|-----------|--------------|
| Admin   | `admin`   | `admin123`   |
| Faculty | `faculty` | `faculty123` |
| Student | `student` | `student123` |

**Heads-up:** the API runs on Render’s free tier, so the first request after idle time can take about a minute while the service wakes up. After that it should feel normal. Opening the health link once before signing in helps.

---

## Run locally

### Docker (easiest)

```bash
docker compose up --build
```

- App → http://localhost:8501  
- API docs → http://localhost:8000/docs  

### Without Docker

**API**

```bash
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

**Web**

```bash
cd web
npm install
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`.

---

## Project layout

```
backend/   FastAPI, SQLAlchemy, seed + sandbox tenants
web/       React institutional UI
docs/      Architecture notes
```

Optional: set `OPENAI_API_KEY` on the API if you want LLM polish on the assistant. Without it, answers still come from database facts only (`grounded` mode).

---

## Deploy notes

- Frontend → **Vercel** (`web/`)  
- API + Postgres → **Render** (`render.yaml`)  
- Production builds expect `VITE_API_BASE_URL` pointing at the Render API (see `web/.env.production`)

---

Built as a learning and portfolio project — feedback welcome.
