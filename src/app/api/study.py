"""
Study session API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import (
    SessionCompleteRequest,
    SessionCompleteResponse,
    SessionStartRequest,
    SessionStartResponse,
)
from app.services.study_session_service import StudySessionService

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/session/complete", response_model=SessionCompleteResponse)
async def complete_study_session(
    request: SessionCompleteRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: CurrentActiveUser,
) -> SessionCompleteResponse:
    """
    Complete a study session and update user statistics.

    Updates:
    - User streak (consecutive study days)
    - Total study time
    - Daily goal progress
    """
    return await StudySessionService.complete_session(
        session=session,
        user=current_user,
        cards_studied=request.cards_studied,
        cards_correct=request.cards_correct,
        duration_seconds=request.duration_seconds,
    )


@router.post("/session/start", response_model=SessionStartResponse)
async def start_study_session(
    request: SessionStartRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: CurrentActiveUser,
) -> SessionStartResponse:
    """
    Start a new study session.

    Returns a mix of new cards (ordered by frequency) and review cards (due for review).

    Parameters:
    - new_cards_limit: Maximum number of new cards to include (default 10)
    - review_cards_limit: Maximum number of review cards to include (default 20)
    """
    return await StudySessionService.start_session(
        session=session,
        user_id=current_user.id,
        new_cards_limit=request.new_cards_limit,
        review_cards_limit=request.review_cards_limit,
    )
