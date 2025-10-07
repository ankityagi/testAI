"""Healthcheck endpoint."""
from fastapi import APIRouter

from .. import deps

router = APIRouter()


@router.get("/healthz", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/reset-cache", tags=["health"])
def reset_cache() -> dict[str, str]:
    deps.reset_repository_cache()
    return {"status": "cache reset"}
