"""Standards listing routes."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query

from .. import deps
from ..db.repository import Repository
from ..models import Parent, Standard

# DEBUG: This prints when module is IMPORTED (should appear on startup)
print("\n" + "="*80, flush=True)
print("🔥 STANDARDS.PY MODULE LOADED - NEW CODE IS ACTIVE 🔥", flush=True)
print("="*80 + "\n", flush=True)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=list[Standard])
def list_standards(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    grade: Optional[int] = Query(None, ge=0, le=12, description="Filter by grade"),
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> list[Standard]:
    # Debug: Verify function is called
    print(f"\n{'='*80}", flush=True)
    print(f"[STANDARDS ENDPOINT HIT] subject={subject}, grade={grade}", flush=True)
    print(f"{'='*80}\n", flush=True)

    logger.info(f"[STANDARDS] Request: subject={subject}, grade={grade}")

    standards = repo.list_standards()
    initial_count = len(standards)
    logger.info(f"[STANDARDS] Initial standards from repo: {initial_count}")

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

        logger.info(f"[STANDARDS] Subject mapping: '{subject}' → '{subject_normalized}' → '{search_subject}'")

        standards = [
            s for s in standards
            if s.get('subject', '').lower() == search_subject
        ]

        logger.info(f"[STANDARDS] After subject filter: {len(standards)} standards")
        if len(standards) > 0:
            # Log sample of subjects found
            sample_subjects = set(s.get('subject') for s in standards[:5])
            logger.info(f"[STANDARDS] Sample subjects in filtered results: {sample_subjects}")

    if grade is not None:
        before_grade_filter = len(standards)
        standards = [s for s in standards if s.get('grade') == grade]
        logger.info(f"[STANDARDS] After grade filter: {len(standards)} standards (was {before_grade_filter})")

        if len(standards) == 0 and before_grade_filter > 0:
            # Log available grades to help debug
            available_grades = set(s.get('grade') for s in repo.list_standards())
            logger.warning(f"[STANDARDS] No standards for grade {grade}. Available grades: {sorted(available_grades)}")

    # Log final result
    logger.info(f"[STANDARDS] Final result: {len(standards)} standards")
    if len(standards) > 0:
        # Log unique domains (topics) for debugging
        domains = set(s.get('domain') for s in standards if s.get('domain'))
        logger.info(f"[STANDARDS] Unique domains in result: {domains}")
    else:
        logger.warning(f"[STANDARDS] Returning empty list - no standards matched filters")

    return [Standard(**entry) for entry in standards]
