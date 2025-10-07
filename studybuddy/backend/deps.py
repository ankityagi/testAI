"""Dependency wiring for database and auth clients."""
from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .db.repository import Repository, build_repository
from .models import Parent

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def get_repository() -> Repository:
    """Return a repository instance (in-memory by default)."""
    return build_repository()


def get_current_parent(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repo: Repository = Depends(get_repository),
) -> Parent:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = credentials.credentials
    parent = repo.get_parent_by_token(token)
    if parent is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return Parent(**parent)


def reset_repository_cache() -> None:
    get_repository.cache_clear()  # type: ignore[attr-defined]
