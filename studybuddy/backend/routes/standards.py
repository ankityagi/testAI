"""Standards listing routes."""
from fastapi import APIRouter, Depends

from .. import deps
from ..db.repository import Repository
from ..models import Parent, Standard

router = APIRouter()


@router.get("/", response_model=list[Standard])
def list_standards(
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> list[Standard]:
    standards = repo.list_standards()
    return [Standard(**entry) for entry in standards]
