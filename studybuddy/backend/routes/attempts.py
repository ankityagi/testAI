"""Attempt logging routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from .. import deps
from ..db.repository import Repository
from ..models import AttemptResult, AttemptSubmission, Parent

router = APIRouter()


@router.post("/", response_model=AttemptResult, status_code=status.HTTP_201_CREATED)
def submit_attempt(
    payload: AttemptSubmission,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> AttemptResult:
    if not repo.child_belongs_to_parent(payload.child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child mismatch")
    try:
        result = repo.log_attempt(
            child_id=payload.child_id,
            question_id=payload.question_id,
            selected=payload.selected,
            time_spent_ms=payload.time_spent_ms,
        )
    except ValueError as exc:
        print(f"[ATTEMPTS] ValueError: {exc}", flush=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AttemptResult(**result)
