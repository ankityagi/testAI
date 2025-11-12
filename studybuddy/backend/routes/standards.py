"""Standards listing routes."""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from .. import deps
from ..db.repository import Repository
from ..models import Parent, Standard

router = APIRouter()


@router.get("/", response_model=list[Standard])
def list_standards(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    grade: Optional[int] = Query(None, ge=0, le=12, description="Filter by grade"),
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> list[Standard]:
    standards = repo.list_standards()

    # Apply filters if provided
    if subject:
        # Normalize subject names for matching
        subject_normalized = subject.lower().strip()

        # Map common variations
        subject_mappings = {
            'mathematics': 'math',
            'english language arts': 'reading',
            'ela': 'reading',
        }

        # Use mapping if available, otherwise use normalized form
        search_subject = subject_mappings.get(subject_normalized, subject_normalized)

        standards = [
            s for s in standards
            if s.get('subject', '').lower() == search_subject
        ]

    if grade is not None:
        standards = [s for s in standards if s.get('grade') == grade]

    return [Standard(**entry) for entry in standards]
