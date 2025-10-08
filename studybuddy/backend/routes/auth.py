"""Authentication routes using repository-backed storage."""
from fastapi import APIRouter, Depends, HTTPException, status

from .. import deps
from ..db.repository import Repository
from ..models import AuthRequest, AuthResponse, Parent

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: AuthRequest, repo: Repository = Depends(deps.get_repository)) -> AuthResponse:
    try:
        result = repo.create_parent(email=payload.email, password=payload.password)
    except ValueError as exc:  # duplicate email
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    parent = Parent(**result["parent"])
    return AuthResponse(access_token=result["token"], parent=parent)


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest, repo: Repository = Depends(deps.get_repository)) -> AuthResponse:
    try:
        result = repo.authenticate_parent(email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc
    parent = Parent(**result["parent"])
    return AuthResponse(access_token=result["token"], parent=parent)
