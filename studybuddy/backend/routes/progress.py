"""Progress reporting routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from .. import deps
from ..db.repository import Repository
from ..models import Parent, ProgressResponse

router = APIRouter()


@router.get("/{child_id}", response_model=ProgressResponse)
def get_progress(
    child_id: str,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> ProgressResponse:
    if not repo.child_belongs_to_parent(child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child mismatch")
    stats = repo.child_progress(child_id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    return ProgressResponse(**stats)
