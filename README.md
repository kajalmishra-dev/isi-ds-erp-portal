# Meridian Campus ERP

Full-stack **academic ERP demo** (fictional institute — not affiliated with any real college):
**FastAPI + PostgreSQL** API and a **React** institutional console.

JWT roles (`admin` / `faculty` / `student`): registrar manages roster / exams / subjects / marks;
faculty take attendance and grade coursework; students view dashboards, marksheets, and the
grounded academic assistant.

## Quick start (Docker)

```bash
docker compose up --build
```

- App: http://localhost:8501
- API docs: http://localhost:8000/docs

### Demo credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Faculty (Y1 programming) | `faculty` | `faculty123` |
| Faculty (frontend) | `faculty2` | `faculty123` |
| Faculty (AI & systems) | `faculty3` | `faculty123` |
| Student (Y1 demo) | `student` | `student123` |

More student logins: `isha`, `rohan`, `vihaan`, `yash`, `priya_s`, … (all `student123`).

Compose currently sets `SEED_RESET=true` so each rebuild refreshes the demo dataset. Set it to
`false` when you want data to persist across restarts.

## Local development

### API

```bash
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

### Web

```bash
cd web
npm install
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`.

## Architecture

```
Browser (React) ──JWT──▶ FastAPI routers ──▶ services ──▶ SQLAlchemy ──▶ PostgreSQL
```

## Notes

- Frontend lives in `web/` (React + Vite + TypeScript).
- Legacy Streamlit UI remains under `frontend/` unused by Compose (archive candidate).
- Empty databases are seeded on API startup. Compose is currently set to `SEED_RESET=true` for fresh demo data on rebuild; switch to `false` to persist edits.
- Architecture notes: [docs/PHASE2_ARCHITECTURE.md](docs/PHASE2_ARCHITECTURE.md).
- Optional LLM polish: set `OPENAI_API_KEY` in the API env. Without it, the assistant still answers from DB facts only (`mode: grounded`).
