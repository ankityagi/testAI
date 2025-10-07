"""Admin endpoints for pre-generating questions."""
import os

from fastapi import APIRouter, Depends, Header, HTTPException, status

from .. import deps
from ..db.repository import Repository
from ..models import AdminGenerateRequest
from ..services.genai import GenerationContext, generate_mcqs

router = APIRouter()


@router.post("/generate")
def admin_generate_questions(
    payload: AdminGenerateRequest,
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
    repo: Repository = Depends(deps.get_repository),
) -> dict:
    expected = os.getenv("STUDYBUDDY_ADMIN_TOKEN")
    if expected and admin_token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")

    ctx = GenerationContext(
        subject=payload.subject,
        topic=payload.topic,
        grade=payload.grade,
        difficulty=payload.difficulty or "medium",
        count=payload.count,
    )
    questions = generate_mcqs(context=ctx)
    repo.insert_questions(questions)
    return {"generated": len(questions)}
