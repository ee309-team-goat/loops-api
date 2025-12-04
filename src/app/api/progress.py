"""
Progress and review API endpoints (FSRS).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import NewCardsCountRead, ReviewRequest, UserCardProgressRead
from app.services.user_card_progress_service import UserCardProgressService

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/review", response_model=UserCardProgressRead)
async def submit_card_review(
    review_data: ReviewRequest,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    Submit a card review.

    - is_correct: true (정답) → FSRS Good rating
    - is_correct: false (오답) → FSRS Again rating
    """
    progress = await UserCardProgressService.process_review(
        session, current_user.id, review_data.card_id, review_data.is_correct
    )
    return progress


@router.get("/due", response_model=list[UserCardProgressRead])
async def get_due_cards(
    limit: int = Query(default=20, ge=1, le=100),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get cards due for review."""
    cards = await UserCardProgressService.get_due_cards(session, current_user.id, limit=limit)
    return cards


@router.get("/{card_id}", response_model=UserCardProgressRead)
async def get_card_progress(
    card_id: int,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get progress for a specific card."""
    progress = await UserCardProgressService.get_user_card_progress(
        session, current_user.id, card_id
    )
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this card",
        )
    return progress


@router.get("/new-cards-count", response_model=NewCardsCountRead)
async def get_new_cards_count(
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get count of new cards and review cards based on user's selected decks."""
    count_data = await UserCardProgressService.get_new_cards_count(session, current_user.id)
    return NewCardsCountRead(**count_data)
