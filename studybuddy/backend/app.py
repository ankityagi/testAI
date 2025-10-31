"""FastAPI entrypoint for studybuddy backend."""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

from .routes import admin, attempts, children, health, progress, questions, quiz, sessions, standards, auth

# Load environment variables from .env file
load_dotenv()
print(f"[APP INIT] STUDYBUDDY_MOCK_AI after load_dotenv: '{os.getenv('STUDYBUDDY_MOCK_AI')}'", flush=True)
print(f"[APP INIT] STUDYBUDDY_DATA_MODE after load_dotenv: '{os.getenv('STUDYBUDDY_DATA_MODE')}'", flush=True)

# React build directory (src/ui/web/dist)
REACT_BUILD_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "ui" / "web" / "dist"
# Legacy static directory
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

    # Mount legacy static files if they exist
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    # Include all API routers
    app.include_router(health.router)
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(children.router, prefix="/children", tags=["children"])
    app.include_router(questions.router, prefix="/questions", tags=["questions"])
    app.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
    app.include_router(progress.router, prefix="/progress", tags=["progress"])
    app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
    app.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
    app.include_router(standards.router, prefix="/standards", tags=["standards"])
    app.include_router(admin.router, prefix="/admin", tags=["admin"])

    # Serve React static assets (JS, CSS, images)
    if REACT_BUILD_DIR.exists():
        app.mount("/assets", StaticFiles(directory=REACT_BUILD_DIR / "assets"), name="react-assets")

        # Catch-all route for React app (must be last)
        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            """
            Serve React app for all non-API routes to support client-side routing.

            This catches all GET requests that don't match API routes above.
            Since API routers are registered first with specific prefixes,
            they take priority over this catch-all route.
            """
            index_file = REACT_BUILD_DIR / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            return {"error": "React app not found"}

    return app


app = create_app()
