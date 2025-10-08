"""Question retrieval routes."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from .. import deps
from ..db.repository import Repository
from ..models import Parent, QuestionRequest, QuestionResponse
from ..services import pacing
from ..services import question_picker as picker

router = APIRouter()


@router.post("/fetch", response_model=QuestionResponse)
def fetch_questions(
    payload: QuestionRequest,
    background_tasks: BackgroundTasks,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> QuestionResponse:
    if not repo.child_belongs_to_parent(payload.child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child mismatch")
    child = repo.get_child(payload.child_id)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    topic = payload.topic
    if not topic:
        grade_value = child.get("grade")
        topic = pacing.first_topic_or_default(
            grade=int(grade_value) if grade_value is not None else 0,
            subject=payload.subject,
            default=None,
        )

    batch = picker.fetch_batch(
        repo=repo,
        child=child,
        subject=payload.subject,
        topic=topic,
        limit=payload.limit,
    )
    if batch.stock_deficit > 0:
        background_tasks.add_task(
            picker.top_up_stock,
            repo=repo,
            child=child,
            subject=payload.subject,
            topic=topic,
            count=batch.stock_deficit,
        )
    return QuestionResponse(questions=batch.questions)
