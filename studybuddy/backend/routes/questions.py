"""Question retrieval routes."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from .. import deps
from ..db.repository import Repository
from ..models import Parent, QuestionRequest, QuestionResponse
from ..services import pacing
from ..services import question_picker as picker

router = APIRouter()


@router.get("/topics")
def list_topics(
    subject: str = Query(...),
    grade: int = Query(...),
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
):
    """List available topics for a given subject/grade combination."""
    # Get all subtopics and extract unique topics
    subtopics = repo.list_subtopics(subject=subject, grade=grade, topic=None)

    # Extract unique topics while preserving order
    seen = set()
    topics = []
    for st in subtopics:
        topic = st.get("topic")
        if topic and topic not in seen:
            seen.add(topic)
            topics.append({"topic": topic})

    return {"topics": topics}


@router.get("/subtopics")
def list_subtopics(
    subject: str = Query(...),
    grade: int = Query(...),
    topic: str = Query(None),
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
):
    """List available subtopics for a given subject/grade/topic combination."""
    subtopics = repo.list_subtopics(subject=subject, grade=grade, topic=topic)
    return {"subtopics": subtopics}


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

    # CONDITIONAL subtopic selection
    subtopic = payload.subtopic
    if subtopic:
        print(f"[ROUTE] Using user-specified subtopic: {subtopic}", flush=True)
    else:
        print(f"[ROUTE] No subtopic specified, will auto-select", flush=True)

    batch = picker.fetch_batch(
        repo=repo,
        child=child,
        subject=payload.subject,
        topic=topic,
        subtopic=subtopic,  # Can be None or user-specified
        limit=payload.limit,
    )

    # CRITICAL: Restock the SPECIFIC subtopic that was used
    if batch.stock_deficit > 0:
        background_tasks.add_task(
            picker.top_up_stock,
            repo=repo,
            child=child,
            subject=payload.subject,
            topic=topic,
            subtopic=batch.selected_subtopic,  # Use the DEPLETED subtopic
            count=batch.stock_deficit,
        )

    return QuestionResponse(
        questions=batch.questions,
        selected_subtopic=batch.selected_subtopic  # Always return what was used
    )
