"""Router package exporting FastAPI routers."""
from . import admin, attempts, children, health, progress, questions, standards, auth  # noqa: F401

__all__ = [
    "admin",
    "attempts",
    "children",
    "health",
    "progress",
    "questions",
    "standards",
    "auth",
]
