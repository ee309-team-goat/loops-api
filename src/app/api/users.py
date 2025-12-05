"""
User-related API endpoints.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import (
    DailyGoalRead,
    StreakRead,
    TodayProgressRead,
    User,
    UserCardProgress,
    UserConfigRead,
    UserConfigUpdate,
    UserLevelRead,
    UserRead,
    UserUpdate,
)
from app.services.user_card_progress_service import UserCardProgressService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: CurrentActiveUser,
) -> User:
    """Get the current authenticated user's profile."""
    return current_user


@router.get("/me/today-progress", response_model=TodayProgressRead)
async def get_today_progress(
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get today's learning progress statistics."""
    progress_data = await UserCardProgressService.get_today_progress(
        session, current_user.id, current_user.daily_goal
    )
    return TodayProgressRead(**progress_data)


@router.get("/me/daily-goal", response_model=DailyGoalRead)
async def get_daily_goal(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Get the current user's daily goal and today's completion count."""
    daily_goal_data = await UserService.get_daily_goal(session, current_user.id)
    if not daily_goal_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return daily_goal_data


@router.get("/me/config", response_model=UserConfigRead)
async def get_user_config(
    current_user: CurrentActiveUser,
) -> UserConfigRead:
    """
    Get user's configuration/settings.

    Returns daily_goal, select_all_decks, timezone, theme, notification_enabled.
    """
    return UserConfigRead(
        daily_goal=current_user.daily_goal,
        select_all_decks=current_user.select_all_decks,
        timezone=current_user.timezone,
        theme=current_user.theme,
        notification_enabled=current_user.notification_enabled,
    )


@router.put("/me/config", response_model=UserConfigRead)
async def update_user_config(
    config_data: UserConfigUpdate,
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserConfigRead:
    """
    Update user's configuration/settings.

    Supports partial updates - only provided fields will be updated.
    """
    # Update only provided fields
    update_data = config_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return UserConfigRead(
        daily_goal=current_user.daily_goal,
        select_all_decks=current_user.select_all_decks,
        timezone=current_user.timezone,
        theme=current_user.theme,
        notification_enabled=current_user.notification_enabled,
    )


@router.get("/me/level", response_model=UserLevelRead)
async def get_user_level(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserLevelRead:
    """
    Get user's calculated proficiency level.

    Based on recent 50 reviews, accuracy rate, and mastered card difficulty.
    Returns level (1.0-10.0) and CEFR equivalent (A1-C2).
    """
    level_data = await UserService.calculate_user_level(session, current_user.id)
    return UserLevelRead(**level_data)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get a user by ID (requires authentication)."""
    user = await UserService.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Update a user (requires authentication)."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    user = await UserService.update_user(session, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Delete a user (requires authentication)."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    success = await UserService.delete_user(session, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return None


@router.get("/me/streak", response_model=StreakRead)
async def get_user_streak(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """
    Get user's streak information.

    Returns current streak, longest streak, and study statistics for this month.
    """
    # Calculate days_studied_this_month
    now = datetime.now(UTC)
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Count distinct dates when user reviewed cards this month
    days_query = select(
        func.count(func.distinct(func.date(UserCardProgress.last_review_date)))
    ).where(
        UserCardProgress.user_id == current_user.id,
        UserCardProgress.last_review_date >= first_day_of_month,
        UserCardProgress.last_review_date.isnot(None),
    )
    result = await session.exec(days_query)
    days_studied_this_month = result.one()

    # Calculate streak_status
    today = now.date()
    yesterday = today - timedelta(days=1)

    if current_user.last_study_date in [today, yesterday]:
        streak_status = "active"
        message = f"🔥 {current_user.current_streak}일 연속 학습 중!"
    else:
        streak_status = "broken"
        if current_user.last_study_date:
            days_ago = (today - current_user.last_study_date).days
            message = f"💪 {days_ago}일 전 마지막 학습. 다시 시작해보세요!"
        else:
            message = "💪 첫 학습을 시작해보세요!"

    return StreakRead(
        current_streak=current_user.current_streak,
        longest_streak=current_user.longest_streak,
        last_study_date=current_user.last_study_date,
        days_studied_this_month=days_studied_this_month,
        streak_status=streak_status,
        message=message,
    )
