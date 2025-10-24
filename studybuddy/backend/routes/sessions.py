"""Session tracking routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from .. import deps
from ..db.repository import Repository
from ..models import Parent, Session, SessionSummary
from ..services.text_utils import to_display_case

router = APIRouter()


@router.get("/{session_id}", response_model=Session)
def get_session(
    session_id: str,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> Session:
    """Get a session by ID."""
    session_data = repo.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Verify the session belongs to a child of this parent
    child_id = session_data.get("child_id")
    if not child_id or not repo.child_belongs_to_parent(child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Format metadata for display
    if session_data.get("subject"):
        session_data["subject"] = to_display_case(session_data["subject"])
    if session_data.get("topic"):
        session_data["topic"] = to_display_case(session_data["topic"])
    if session_data.get("subtopic"):
        session_data["subtopic"] = to_display_case(session_data["subtopic"])

    return Session(**session_data)


@router.get("/{session_id}/summary", response_model=SessionSummary)
def get_session_summary(
    session_id: str,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> SessionSummary:
    """Get summary statistics for a session."""
    # First verify access
    session_data = repo.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    child_id = session_data.get("child_id")
    if not child_id or not repo.child_belongs_to_parent(child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Get summary statistics
    summary_data = repo.get_session_summary(session_id)

    # Format session metadata for display
    if "session" in summary_data and summary_data["session"]:
        session = summary_data["session"]
        if session.get("subject"):
            session["subject"] = to_display_case(session["subject"])
        if session.get("topic"):
            session["topic"] = to_display_case(session["topic"])
        if session.get("subtopic"):
            session["subtopic"] = to_display_case(session["subtopic"])

    return SessionSummary(**summary_data)


@router.post("/{session_id}/end", response_model=Session)
def end_session(
    session_id: str,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> Session:
    """End a practice session."""
    # First verify access
    session_data = repo.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    child_id = session_data.get("child_id")
    if not child_id or not repo.child_belongs_to_parent(child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # End the session
    try:
        ended_session = repo.end_session(session_id)

        # Format metadata for display
        if ended_session.get("subject"):
            ended_session["subject"] = to_display_case(ended_session["subject"])
        if ended_session.get("topic"):
            ended_session["topic"] = to_display_case(ended_session["topic"])
        if ended_session.get("subtopic"):
            ended_session["subtopic"] = to_display_case(ended_session["subtopic"])

        return Session(**ended_session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
