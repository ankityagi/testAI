"""FastAPI entrypoint for studybuddy backend."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from .routes import admin, attempts, children, health, progress, questions, standards, auth

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="studybuddy", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(children.router, prefix="/children", tags=["children"])
    app.include_router(questions.router, prefix="/questions", tags=["questions"])
    app.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
    app.include_router(progress.router, prefix="/progress", tags=["progress"])
    app.include_router(standards.router, prefix="/standards", tags=["standards"])
    app.include_router(admin.router, prefix="/admin", tags=["admin"])

    return app


app = create_app()
