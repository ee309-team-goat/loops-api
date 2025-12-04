"""
Stats-related API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import UserCardProgress, VocabularyCard
from app.models.enums import CardState
from app.models.schemas.stats import TotalLearnedRead

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/total-learned", response_model=TotalLearnedRead)
async def get_total_learned(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """Get total learned cards statistics with breakdown by CEFR level."""

    # Count total REVIEW state cards
    total_learned_query = select(func.count(UserCardProgress.id)).where(
        UserCardProgress.user_id == current_user.id,
        UserCardProgress.card_state == CardState.REVIEW,
    )
    result = await session.exec(total_learned_query)
    total_learned = result.one()

    # Get breakdown by CEFR level
    by_level_query = (
        select(VocabularyCard.cefr_level, func.count(UserCardProgress.id))
        .select_from(UserCardProgress)
        .join(
            VocabularyCard,
            VocabularyCard.id == UserCardProgress.card_id,
        )
        .where(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.card_state == CardState.REVIEW,
            VocabularyCard.cefr_level.isnot(None),
        )
        .group_by(VocabularyCard.cefr_level)
    )
    result = await session.exec(by_level_query)
    by_level_results = result.all()

    # Convert to dictionary
    by_level = dict(by_level_results)

    return TotalLearnedRead(
        total_learned=total_learned,
        by_level=by_level,
        total_study_time_minutes=current_user.total_study_time_minutes,
    )
