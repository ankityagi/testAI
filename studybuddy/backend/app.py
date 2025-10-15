"""FastAPI entrypoint for studybuddy backend."""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from .routes import admin, attempts, children, health, progress, questions, standards, auth

# Load environment variables from .env file
load_dotenv()
print(f"[APP INIT] STUDYBUDDY_MOCK_AI after load_dotenv: '{os.getenv('STUDYBUDDY_MOCK_AI')}'", flush=True)
print(f"[APP INIT] STUDYBUDDY_DATA_MODE after load_dotenv: '{os.getenv('STUDYBUDDY_DATA_MODE')}'", flush=True)

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
