"""Quiz mode routes."""
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from .. import deps
from ..db.repository import Repository
from ..models import (
    DifficultyMix,
    Parent,
    QuizCreateRequest,
    QuizIncorrectItem,
    QuizQuestionDisplay,
    QuizResult,
    QuizSession,
    QuizSessionResponse,
    QuizSubmitRequest,
)
from ..services.quiz_grading import grade_quiz
from ..services.quiz_selection import select_quiz_questions

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sessions", response_model=QuizSessionResponse, status_code=status.HTTP_201_CREATED)
def create_quiz_session(
    payload: QuizCreateRequest,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> QuizSessionResponse:
    """
    Create a new quiz session.

    Validates:
    - child_id belongs to authenticated parent
    - No active quiz exists for same child/subject/topic
    - Sufficient questions available
    """
    logger.info(f"[QUIZ] Creating quiz for child {payload.child_id}, subject {payload.subject}, topic {payload.topic}")

    # Validate child belongs to parent
    if not repo.child_belongs_to_parent(payload.child_id, parent.id):
        logger.warning(f"[QUIZ] Auth failed: child {payload.child_id} doesn't belong to parent {parent.id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child does not belong to parent")

    # Check for active quiz
    active_quiz = repo.check_active_quiz(payload.child_id, payload.subject, payload.topic)
    if active_quiz:
        logger.warning(f"[QUIZ] Active quiz already exists: {active_quiz['id']}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Active quiz already exists for this child/subject/topic: {active_quiz['id']}"
        )

    # Get child details
    child = repo.get_child(payload.child_id)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    grade = child.get("grade")

    # Prepare difficulty mix
    difficulty_mix = payload.difficulty_mix or DifficultyMix()
    mix_dict = {
        "easy": difficulty_mix.easy,
        "medium": difficulty_mix.medium,
        "hard": difficulty_mix.hard
    }

    # Select questions
    try:
        selection_result = select_quiz_questions(
            repo=repo,
            child_id=payload.child_id,
            subject=payload.subject,
            topic=payload.topic,
            subtopic=payload.subtopic,
            grade=grade,
            question_count=payload.question_count,
            difficulty_mix=mix_dict
        )
    except ValueError as e:
        logger.error(f"[QUIZ] Question selection failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    questions = selection_result.questions

    # Create quiz session
    session = repo.create_quiz_session(
        child_id=payload.child_id,
        subject=payload.subject,
        topic=payload.topic,
        subtopic=payload.subtopic,
        question_count=payload.question_count,
        duration_sec=payload.duration_sec,
        difficulty_mix=mix_dict
    )

    logger.info(f"[QUIZ] Created session {session['id']}")

    # Store questions
    quiz_questions = [
        {
            "question_id": q["id"],
            "index": idx,
            "correct_choice": q["correct_answer"],
            "explanation": q.get("rationale", ""),
        }
        for idx, q in enumerate(questions)
    ]

    repo.create_quiz_session_questions(session["id"], quiz_questions)

    logger.info(f"[QUIZ] Stored {len(quiz_questions)} questions for session {session['id']}")

    # Prepare response (hide correct answers)
    question_displays = [
        QuizQuestionDisplay(
            id=q["id"],
            index=idx,
            stem=q["stem"],
            options=q["options"],
            difficulty=q.get("difficulty"),
            subject=q["subject"],
            topic=q.get("topic")
        )
        for idx, q in enumerate(questions)
    ]

    return QuizSessionResponse(
        session=QuizSession(**session),
        questions=question_displays,
        time_remaining_sec=payload.duration_sec
    )


@router.get("/sessions", response_model=list[QuizSession])
def list_quiz_sessions(
    child_id: str,
    limit: int = 20,
    offset: int = 0,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> list[QuizSession]:
    """List quiz sessions for a child."""
    # Validate child belongs to parent
    if not repo.child_belongs_to_parent(child_id, parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child does not belong to parent")

    sessions = repo.list_quiz_sessions(child_id, limit=limit, offset=offset)
    return [QuizSession(**s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=QuizSessionResponse)
def get_quiz_session(
    session_id: str,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> QuizSessionResponse:
    """
    Get quiz session details.

    Returns:
    - Session metadata
    - Questions (without correct answers if not yet submitted)
    - Remaining time
    """
    session = repo.get_quiz_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz session not found")

    # Validate child belongs to parent
    if not repo.child_belongs_to_parent(session["child_id"], parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Auto-expire if older than 24 hours
    created_at = session["created_at"]
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

    if session["status"] == "active" and datetime.utcnow() > created_at + timedelta(hours=24):
        logger.info(f"[QUIZ] Auto-expiring session {session_id} (>24h old)")
        repo.expire_quiz_session(session_id)
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Quiz session has expired")

    # Get questions
    questions = repo.get_quiz_session_questions(session_id)

    # Calculate remaining time
    started_at = session["started_at"]
    if isinstance(started_at, str):
        started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))

    elapsed_sec = int((datetime.utcnow() - started_at).total_seconds())
    time_remaining_sec = max(0, session["duration_sec"] - elapsed_sec)

    # Prepare question display (hide answers if not submitted)
    if session["status"] != "completed":
        question_displays = [
            QuizQuestionDisplay(
                id=q["question_id"],
                index=q["index"],
                stem=q["stem"],
                options=q["options"],
                difficulty=q.get("difficulty"),
                subject=q["subject"],
                topic=q.get("topic")
            )
            for q in questions
        ]
    else:
        # For completed quizzes, we can show more details in separate endpoint
        question_displays = [
            QuizQuestionDisplay(
                id=q["question_id"],
                index=q["index"],
                stem=q["stem"],
                options=q["options"],
                difficulty=q.get("difficulty"),
                subject=q["subject"],
                topic=q.get("topic")
            )
            for q in questions
        ]

    return QuizSessionResponse(
        session=QuizSession(**session),
        questions=question_displays,
        time_remaining_sec=time_remaining_sec
    )


@router.post("/sessions/{session_id}/submit", response_model=QuizResult)
def submit_quiz(
    session_id: str,
    payload: QuizSubmitRequest,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> QuizResult:
    """
    Submit quiz answers and receive graded results.

    Returns:
    - Score
    - Incorrect items with explanations
    """
    logger.info(f"[QUIZ] Submitting quiz {session_id}")

    session = repo.get_quiz_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz session not found")

    # Validate child belongs to parent
    if not repo.child_belongs_to_parent(session["child_id"], parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Check if already submitted
    if session["status"] == "completed":
        logger.warning(f"[QUIZ] Session {session_id} already submitted")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz already submitted")

    # Check if expired
    if session["status"] == "expired":
        logger.warning(f"[QUIZ] Session {session_id} is expired")
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Quiz session has expired")

    # Get questions
    questions = repo.get_quiz_session_questions(session_id)

    # Grade quiz
    grading_result = grade_quiz(
        session=session,
        questions=questions,
        answers=[ans.model_dump() for ans in payload.answers]
    )

    # Submit to repo
    answers_list = [{"question_id": ans.question_id, "selected_choice": ans.selected_choice} for ans in payload.answers]
    updated_session = repo.submit_quiz_session(session_id, answers_list)

    logger.info(f"[QUIZ] Quiz {session_id} graded: {grading_result.score}%")

    # Prepare result
    incorrect_items = [
        QuizIncorrectItem(**item) for item in grading_result.incorrect_items
    ]

    return QuizResult(
        session_id=session_id,
        score=grading_result.score,
        correct_count=grading_result.correct_count,
        total_questions=grading_result.total_questions,
        time_taken_sec=grading_result.time_taken_sec,
        incorrect_items=incorrect_items,
        submitted_at=updated_session["submitted_at"]
    )


@router.post("/sessions/{session_id}/expire", response_model=QuizSession)
def expire_quiz(
    session_id: str,
    parent: Parent = Depends(deps.get_current_parent),
    repo: Repository = Depends(deps.get_repository),
) -> QuizSession:
    """Mark a quiz session as expired."""
    logger.info(f"[QUIZ] Expiring session {session_id}")

    session = repo.get_quiz_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz session not found")

    # Validate child belongs to parent
    if not repo.child_belongs_to_parent(session["child_id"], parent.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    expired_session = repo.expire_quiz_session(session_id)
    if not expired_session:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session cannot be expired")

    return QuizSession(**expired_session)
