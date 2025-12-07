"""
사용자 관련 API 엔드포인트.

프로필 조회/수정, 학습 설정, 스트릭 정보, 레벨 정보 등 사용자 데이터를 관리합니다.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
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

TAG = "users"
TAG_METADATA = {
    "name": TAG,
    "description": "사용자 관련 API. 프로필 조회/수정, 학습 설정, 스트릭 정보, 레벨 정보 등 사용자 데이터를 관리합니다.",
}

router = APIRouter(prefix="/users", tags=[TAG])


@router.get(
    "/me",
    response_model=UserRead,
    summary="내 프로필 조회",
    description="현재 인증된 사용자의 프로필 정보를 반환합니다.",
    responses={
        200: {"description": "프로필 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_current_user_profile(
    current_user: CurrentActiveUser,
) -> User:
    """
    현재 인증된 사용자의 프로필을 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - 기본 정보: ID, 이메일, 사용자명
    - 학습 설정: 일일 목표, 덱 선택 설정, 테마
    - 스트릭: 현재/최장 연속 학습일
    - 통계: 총 학습 시간
    """
    return current_user


@router.get(
    "/me/today-progress",
    response_model=TodayProgressRead,
    summary="오늘의 학습 진행 상황",
    description="오늘 학습한 카드 수와 일일 목표 달성률을 반환합니다.",
    responses={
        200: {"description": "오늘의 학습 진행 상황 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_today_progress(
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    오늘의 학습 진행 상황을 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `cards_studied_today`: 오늘 학습한 카드 수
    - `daily_goal`: 일일 목표 카드 수
    - `progress_percent`: 목표 달성률 (%)
    - `is_goal_completed`: 목표 달성 여부
    """
    progress_data = await UserCardProgressService.get_today_progress(
        session, current_user.id, current_user.daily_goal
    )
    return TodayProgressRead(**progress_data)


@router.get(
    "/me/daily-goal",
    response_model=DailyGoalRead,
    summary="일일 목표 조회",
    description="사용자의 일일 학습 목표와 오늘 완료한 카드 수를 반환합니다.",
    responses={
        200: {"description": "일일 목표 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "사용자를 찾을 수 없음"},
    },
)
async def get_daily_goal(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """
    일일 학습 목표 정보를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `daily_goal`: 설정된 일일 목표 카드 수
    - `completed_today`: 오늘 학습 완료한 카드 수
    """
    daily_goal_data = await UserService.get_daily_goal(session, current_user.id)
    if not daily_goal_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return daily_goal_data


@router.get(
    "/me/config",
    response_model=UserConfigRead,
    summary="사용자 설정 조회",
    description="사용자의 학습 설정 및 앱 설정을 반환합니다.",
    responses={
        200: {"description": "사용자 설정 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_user_config(
    current_user: CurrentActiveUser,
) -> UserConfigRead:
    """
    사용자 설정을 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `daily_goal`: 일일 학습 목표 카드 수
    - `select_all_decks`: 전체 덱 선택 여부
    - `timezone`: 사용자 타임존
    - `theme`: 앱 테마 (light/dark/auto)
    - `notification_enabled`: 알림 활성화 여부
    """
    return UserConfigRead(
        daily_goal=current_user.daily_goal,
        select_all_decks=current_user.select_all_decks,
        timezone=current_user.timezone,
        theme=current_user.theme,
        notification_enabled=current_user.notification_enabled,
    )


@router.put(
    "/me/config",
    response_model=UserConfigRead,
    summary="사용자 설정 수정",
    description="사용자의 학습 설정 및 앱 설정을 수정합니다. 부분 업데이트를 지원합니다.",
    responses={
        200: {"description": "설정 수정 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 값 (예: theme이 허용되지 않는 값)"},
    },
)
async def update_user_config(
    config_data: UserConfigUpdate,
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserConfigRead:
    """
    사용자 설정을 수정합니다.

    **인증 필요:** Bearer 토큰

    **부분 업데이트:** 변경하고 싶은 필드만 전송하면 됩니다.

    **수정 가능한 필드:**
    - `daily_goal`: 1~1000 사이의 정수
    - `select_all_decks`: true/false
    - `timezone`: 타임존 문자열 (예: "Asia/Seoul")
    - `theme`: "light", "dark", "auto" 중 하나
    - `notification_enabled`: true/false
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


@router.get(
    "/me/level",
    response_model=UserLevelRead,
    summary="사용자 레벨 조회",
    description="사용자의 학습 숙련도 레벨과 CEFR 등급을 계산하여 반환합니다.",
    responses={
        200: {"description": "레벨 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_user_level(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserLevelRead:
    """
    사용자의 학습 숙련도 레벨을 조회합니다.

    **인증 필요:** Bearer 토큰

    **계산 기준:**
    - 최근 50회 복습 결과
    - 전체 정확도
    - 마스터한 카드의 난이도 분포

    **반환 정보:**
    - `level`: 숙련도 레벨 (1.0 ~ 10.0)
    - `cefr_equivalent`: CEFR 등급 (A1, A2, B1, B2, C1, C2)
    - `total_reviews`: 총 복습 횟수
    - `accuracy_rate`: 전체 정확도 (%)
    - `mastered_cards`: 마스터한 카드 수
    """
    level_data = await UserService.calculate_user_level(session, current_user.id)
    return UserLevelRead(**level_data)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="특정 사용자 조회",
    description="사용자 ID로 특정 사용자의 프로필을 조회합니다.",
    responses={
        200: {"description": "사용자 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "사용자를 찾을 수 없음"},
    },
)
async def get_user(
    user_id: int = Path(description="조회할 사용자의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    특정 사용자의 프로필을 조회합니다.

    **인증 필요:** Bearer 토큰

    **파라미터:**
    - `user_id`: 조회할 사용자의 ID

    **반환 정보:**
    - 기본 정보: ID, 이메일, 사용자명
    - 학습 설정 및 통계
    """
    user = await UserService.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="사용자 정보 수정",
    description="사용자 정보를 수정합니다. 본인의 정보만 수정 가능합니다.",
    responses={
        200: {"description": "사용자 정보 수정 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        403: {"description": "권한 없음 - 다른 사용자의 정보는 수정할 수 없음"},
        404: {"description": "사용자를 찾을 수 없음"},
        422: {"description": "유효성 검사 실패 - 잘못된 데이터 형식"},
    },
)
async def update_user(
    user_data: UserUpdate,
    user_id: int = Path(description="수정할 사용자의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    사용자 정보를 수정합니다.

    **인증 필요:** Bearer 토큰

    **권한:** 본인의 정보만 수정 가능

    **수정 가능한 필드:**
    - `email`: 이메일 주소
    - `username`: 사용자명 (3자 이상)
    - `is_active`: 활성화 상태
    - `daily_goal`: 일일 목표 (1~1000)
    - `timezone`: 타임존
    - `theme`: 테마 (light/dark/auto)
    - `notification_enabled`: 알림 설정
    """
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


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제",
    description="사용자 계정을 삭제합니다. 본인의 계정만 삭제 가능합니다.",
    responses={
        204: {"description": "사용자 삭제 성공 (응답 본문 없음)"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        403: {"description": "권한 없음 - 다른 사용자의 계정은 삭제할 수 없음"},
        404: {"description": "사용자를 찾을 수 없음"},
    },
)
async def delete_user(
    user_id: int = Path(description="삭제할 사용자의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    사용자 계정을 삭제합니다.

    **인증 필요:** Bearer 토큰

    **권한:** 본인의 계정만 삭제 가능

    **주의사항:**
    - 이 작업은 되돌릴 수 없습니다
    - 사용자의 모든 학습 데이터가 함께 삭제됩니다
    """
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


@router.get(
    "/me/streak",
    response_model=StreakRead,
    summary="스트릭 정보 조회",
    description="사용자의 연속 학습 스트릭 정보와 이번 달 학습 통계를 반환합니다.",
    responses={
        200: {"description": "스트릭 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_user_streak(
    current_user: CurrentActiveUser,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """
    스트릭 정보를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `current_streak`: 현재 연속 학습일 수
    - `longest_streak`: 최장 연속 학습일 수
    - `last_study_date`: 마지막 학습 날짜
    - `days_studied_this_month`: 이번 달 학습한 일수
    - `streak_status`: 스트릭 상태 ("active" 또는 "broken")
    - `message`: 사용자에게 표시할 동기 부여 메시지
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
