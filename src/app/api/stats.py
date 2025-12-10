"""
통계 관련 API 엔드포인트.

총 학습량, 학습 기록, 정확도 통계 등 학습 분석 데이터를 제공합니다.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import UserCardProgress, VocabularyCard
from app.models.enums import CardState
from app.models.schemas.stats import (
    AccuracyByPeriod,
    StatsAccuracyRead,
    StatsHistoryItem,
    StatsHistoryRead,
    TodayStatsRead,
    TodayVocabularyStats,
    TotalLearnedRead,
)
from app.models.tables.study_session import StudySession

TAG = "stats"
TAG_METADATA = {
    "name": TAG,
    "description": "통계 관련 API. 총 학습량, 학습 기록, 정확도 통계 등 학습 분석 데이터를 제공합니다.",
}

router = APIRouter(prefix="/stats", tags=[TAG])


@router.get(
    "/total-learned",
    response_model=TotalLearnedRead,
    summary="총 학습량 통계",
    description="전체 학습 완료 카드 수와 CEFR 레벨별 분류를 반환합니다.",
    responses={
        200: {"description": "총 학습량 통계 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_total_learned(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    총 학습량 통계를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `total_learned`: 학습 완료한 총 카드 수 (REVIEW 상태)
    - `by_level`: CEFR 레벨별 학습 완료 카드 수 (A1, A2, B1, B2, C1, C2)
    - `total_study_time_minutes`: 총 학습 시간 (분)

    **학습 완료 기준:**
    - 카드 상태가 REVIEW인 카드 (FSRS 알고리즘에서 장기 기억으로 분류)
    """

    # Count total REVIEW state cards
    total_learned_query = select(func.count(UserCardProgress.id)).where(
        UserCardProgress.user_id == current_profile.id,
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
            UserCardProgress.user_id == current_profile.id,
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
        total_study_time_minutes=current_profile.total_study_time_minutes,
    )


@router.get(
    "/history",
    response_model=StatsHistoryRead,
    summary="학습 기록 조회",
    description="기간별 일일 학습 기록을 반환합니다. 차트 데이터로 사용할 수 있습니다.",
    responses={
        200: {"description": "학습 기록 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_stats_history(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
    period: Literal["7d", "30d", "90d", "1y"] = Query(
        default="30d",
        description="조회 기간. 7d(7일), 30d(30일), 90d(90일), 1y(1년) 중 선택",
    ),
):
    """
    기간별 학습 기록을 조회합니다.

    **인증 필요:** Bearer 토큰

    **쿼리 파라미터:**
    - `period`: 조회 기간
      - `7d`: 최근 7일
      - `30d`: 최근 30일 (기본값)
      - `90d`: 최근 90일
      - `1y`: 최근 1년

    **반환 정보 (일별):**
    - `date`: 날짜
    - `cards_studied`: 학습한 카드 수
    - `correct_count`: 정답 수
    - `accuracy_rate`: 정확도 (%)

    **용도:**
    - 학습 추이 그래프
    - 일별 학습량 비교
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
            UserCardProgress.user_id == current_profile.id,
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


@router.get(
    "/accuracy",
    response_model=StatsAccuracyRead,
    summary="정확도 통계",
    description="전체 정확도, 기간별 정확도, CEFR 레벨별 정확도를 반환합니다.",
    responses={
        200: {"description": "정확도 통계 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_stats_accuracy(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    정확도 통계를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `overall_accuracy`: 전체 정확도 (%)
    - `total_reviews`: 총 복습 횟수
    - `total_correct`: 총 정답 수
    - `by_period`: 기간별 정확도
      - `all_time`: 전체 기간
      - `last_7_days`: 최근 7일
      - `last_30_days`: 최근 30일
      - `last_90_days`: 최근 90일
    - `by_cefr_level`: CEFR 레벨별 정확도 (A1~C2)
    - `trend`: 추세 ("improving", "stable", "declining")

    **추세 계산 기준:**
    - 최근 7일 정확도와 그 이전 7일 정확도 비교
    - 5% 이상 상승: improving
    - 5% 이상 하락: declining
    - 그 외: stable
    """
    now = datetime.now(UTC)

    # Helper function to calculate accuracy for a period
    async def get_accuracy_for_period(days: int | None) -> tuple[int, int]:
        """Returns (total_reviews, correct_count) for the given period."""
        query = select(
            func.sum(UserCardProgress.total_reviews),
            func.sum(UserCardProgress.correct_count),
        ).where(UserCardProgress.user_id == current_profile.id)

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
            UserCardProgress.user_id == current_profile.id,
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
            UserCardProgress.user_id == current_profile.id,
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


@router.get(
    "/today",
    response_model=TodayStatsRead,
    summary="오늘의 학습 정보",
    description="오늘 하루 동안의 학습 통계를 반환합니다. 총 학습 시간, 학습 문제 수, 신규/복습 카드 수, 정답률, 일일 목표 진행률 등을 포함합니다.",
    responses={
        200: {"description": "오늘의 학습 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_today_stats(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    오늘의 학습 정보를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `total_study_time_seconds`: 오늘 학습한 총 시간 (초 단위)
    - `total_cards_studied`: 오늘 학습한 총 문제 수
    - `vocabulary`: 어휘 학습 상세 통계
      - `new_cards_count`: 오늘 학습한 신규 카드 수
      - `review_cards_count`: 오늘 학습한 복습 카드 수
      - `review_accuracy`: 오늘 복습 카드의 정답률 (%, 복습 카드가 없으면 null)
      - `progress`: 일일 목표 대비 진행률 (0-100%)
      - `daily_goal`: 일일 학습 목표 카드 수

    **오늘 기준:**
    - UTC 기준 오늘 날짜 (00:00:00 ~ 23:59:59)
    """
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Query today's completed study sessions
    sessions_query = select(StudySession).where(
        StudySession.user_id == current_profile.id,
        StudySession.started_at >= today_start,
        StudySession.started_at <= today_end,
        StudySession.completed_at.isnot(None),  # Only completed sessions
    )
    result = await session.exec(sessions_query)
    sessions = result.all()

    # Calculate totals
    total_study_time_seconds = 0
    total_cards_studied = 0
    new_cards_count = 0
    review_cards_count = 0
    review_correct_count = 0

    for study_session in sessions:
        # Calculate study time
        if study_session.completed_at and study_session.started_at:
            duration = (study_session.completed_at - study_session.started_at).total_seconds()
            total_study_time_seconds += int(duration)

        # Sum cards
        cards_in_session = study_session.correct_count + study_session.wrong_count
        total_cards_studied += cards_in_session
        new_cards_count += study_session.new_cards_count
        review_cards_count += study_session.review_cards_count

        # For review accuracy, we need to know which cards were reviews and their correctness
        # Assuming review cards are tracked in review_cards_count
        # and correct_count applies proportionally
        if study_session.review_cards_count > 0:
            # Proportion of correct answers from review cards
            # This is an approximation since we don't track separately
            session_accuracy = (
                study_session.correct_count / cards_in_session if cards_in_session > 0 else 0
            )
            review_correct_count += int(
                study_session.review_cards_count * session_accuracy
            )

    # Calculate review accuracy
    review_accuracy = None
    if review_cards_count > 0:
        review_accuracy = round((review_correct_count / review_cards_count) * 100, 1)

    # Get daily goal from profile
    daily_goal = current_profile.daily_goal or 30  # Default to 30 if not set

    # Calculate progress
    progress = min((total_cards_studied / daily_goal) * 100, 100.0) if daily_goal > 0 else 0.0

    vocabulary_stats = TodayVocabularyStats(
        new_cards_count=new_cards_count,
        review_cards_count=review_cards_count,
        review_accuracy=review_accuracy,
        progress=round(progress, 1),
        daily_goal=daily_goal,
    )

    return TodayStatsRead(
        total_study_time_seconds=total_study_time_seconds,
        total_cards_studied=total_cards_studied,
        vocabulary=vocabulary_stats,
    )
