"""Children management routes."""
from fastapi import APIRouter, Depends, HTTPException, Response, status

from .. import deps
from ..db.repository import Repository
from ..models import Child, ChildCreate, ChildUpdate, Parent

router = APIRouter()


@router.get("/", response_model=list[Child])
def list_children(
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> list[Child]:
    children = repo.list_children(parent.id)
    return [Child(**child) for child in children]


@router.post("/", response_model=Child, status_code=status.HTTP_201_CREATED)
def create_child(
    payload: ChildCreate,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> Child:
    record = repo.create_child(parent.id, payload.model_dump())
    return Child(**record)


@router.patch("/{child_id}", response_model=Child)
def update_child(
    child_id: str,
    payload: ChildUpdate,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> Child:
    if not repo.child_belongs_to_parent(child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child mismatch")
    update_payload = payload.model_dump(exclude_unset=True)
    if "birthdate" in update_payload and update_payload["birthdate"]:
        update_payload["birthdate"] = str(update_payload["birthdate"])
    try:
        record = repo.update_child(child_id, update_payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Child(**record)


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    child_id: str,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> Response:
    if not repo.child_belongs_to_parent(child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child mismatch")
    try:
        repo.delete_child(child_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
