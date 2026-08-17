# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import admin, auth, student

app = FastAPI(title=settings.APP_NAME, version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(student.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
