from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.core.config import APP_NAME
from backend.database.db import init_db

app = FastAPI(title=APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "docs": "/docs",
        "reports": "/api/reports",
        "description": "FastAPI + SQLite + Multi-Agent + 飞书风格报告页面",
    }


app.include_router(router, prefix="/api")
# 同时挂一个非 API 前缀，方便飞书报告页面访问
app.include_router(router)
