"""
Stats-related API endpoints.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import UserCardProgress, VocabularyCard
from app.models.enums import CardState
from app.models.schemas.stats import (
    AccuracyByPeriod,
    StatsAccuracyRead,
    StatsHistoryItem,
    StatsHistoryRead,
    TotalLearnedRead,
)

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


@router.get("/history", response_model=StatsHistoryRead)
async def get_stats_history(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    period: Literal["7d", "30d", "90d", "1y"] = Query(default="30d", description="Time period"),
):
    """
    Get study history for charts.

    Returns daily statistics including cards studied, correct count, and accuracy rate.
    """
    # Calculate date range based on period
    now = datetime.now(UTC)
    period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = period_days[period]
    start_date = now - timedelta(days=days)

    # Query for daily stats grouped by date
    # Using correct_count and total_reviews from UserCardProgress
    history_query = (
        select(
            func.date(UserCardProgress.last_review_date).label("review_date"),
            func.sum(UserCardProgress.total_reviews).label("cards_studied"),
            func.sum(UserCardProgress.correct_count).label("correct_count"),
        )
        .where(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.last_review_date >= start_date,
            UserCardProgress.last_review_date.isnot(None),
        )
        .group_by(func.date(UserCardProgress.last_review_date))
        .order_by(func.date(UserCardProgress.last_review_date).asc())
    )

    result = await session.exec(history_query)
    rows = result.all()

    # Build history items
    history_data = []
    for row in rows:
        review_date, cards_studied, correct_count = row
        cards_studied = cards_studied or 0
        correct_count = correct_count or 0
        accuracy = (correct_count / cards_studied * 100) if cards_studied > 0 else 0.0

        history_data.append(
            StatsHistoryItem(
                date=review_date,
                cards_studied=cards_studied,
                correct_count=correct_count,
                accuracy_rate=round(accuracy, 1),
            )
        )

    return StatsHistoryRead(period=period, data=history_data)


@router.get("/accuracy", response_model=StatsAccuracyRead)
async def get_stats_accuracy(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Get accuracy statistics.

    Returns overall accuracy, accuracy by time period, and accuracy by CEFR level.
    """
    now = datetime.now(UTC)

    # Helper function to calculate accuracy for a period
    async def get_accuracy_for_period(days: int | None) -> tuple[int, int]:
        """Returns (total_reviews, correct_count) for the given period."""
        query = select(
            func.sum(UserCardProgress.total_reviews),
            func.sum(UserCardProgress.correct_count),
        ).where(UserCardProgress.user_id == current_user.id)

        if days is not None:
            start_date = now - timedelta(days=days)
            query = query.where(UserCardProgress.last_review_date >= start_date)

        result = await session.exec(query)
        row = result.one()
        return (row[0] or 0, row[1] or 0)

    # Get all-time stats
    total_reviews, total_correct = await get_accuracy_for_period(None)
    overall_accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0.0

    # Get period-based stats
    reviews_7d, correct_7d = await get_accuracy_for_period(7)
    reviews_30d, correct_30d = await get_accuracy_for_period(30)
    reviews_90d, correct_90d = await get_accuracy_for_period(90)

    accuracy_7d = (correct_7d / reviews_7d * 100) if reviews_7d > 0 else None
    accuracy_30d = (correct_30d / reviews_30d * 100) if reviews_30d > 0 else None
    accuracy_90d = (correct_90d / reviews_90d * 100) if reviews_90d > 0 else None

    by_period = AccuracyByPeriod(
        all_time=round(overall_accuracy, 1),
        last_7_days=round(accuracy_7d, 1) if accuracy_7d is not None else None,
        last_30_days=round(accuracy_30d, 1) if accuracy_30d is not None else None,
        last_90_days=round(accuracy_90d, 1) if accuracy_90d is not None else None,
    )

    # Get accuracy by CEFR level
    by_level_query = (
        select(
            VocabularyCard.cefr_level,
            func.sum(UserCardProgress.total_reviews),
            func.sum(UserCardProgress.correct_count),
        )
        .select_from(UserCardProgress)
        .join(VocabularyCard, VocabularyCard.id == UserCardProgress.card_id)
        .where(
            UserCardProgress.user_id == current_user.id,
            VocabularyCard.cefr_level.isnot(None),
        )
        .group_by(VocabularyCard.cefr_level)
    )
    result = await session.exec(by_level_query)
    by_level_rows = result.all()

    by_cefr_level = {}
    for level, reviews, correct in by_level_rows:
        if reviews and reviews > 0:
            by_cefr_level[level] = round((correct or 0) / reviews * 100, 1)

    # Determine trend (comparing last 7 days vs previous 7 days)
    trend = "stable"
    if accuracy_7d is not None:
        # Get accuracy for 8-14 days ago
        prev_start = now - timedelta(days=14)
        prev_end = now - timedelta(days=7)
        prev_query = select(
            func.sum(UserCardProgress.total_reviews),
            func.sum(UserCardProgress.correct_count),
        ).where(
            UserCardProgress.user_id == current_user.id,
            UserCardProgress.last_review_date >= prev_start,
            UserCardProgress.last_review_date < prev_end,
        )
        result = await session.exec(prev_query)
        prev_row = result.one()
        prev_reviews, prev_correct = prev_row[0] or 0, prev_row[1] or 0

        if prev_reviews > 0:
            prev_accuracy = prev_correct / prev_reviews * 100
            diff = accuracy_7d - prev_accuracy
            if diff > 5:
                trend = "improving"
            elif diff < -5:
                trend = "declining"

    return StatsAccuracyRead(
        overall_accuracy=round(overall_accuracy, 1),
        total_reviews=total_reviews,
        total_correct=total_correct,
        by_period=by_period,
        by_cefr_level=by_cefr_level,
        trend=trend,
    )
