"""
학습 진행 및 복습 관련 API 엔드포인트.

FSRS(Free Spaced Repetition Scheduler) 알고리즘 기반의 카드 복습 및 학습 진도 관리를 처리합니다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import NewCardsCountRead, ReviewRequest, UserCardProgressRead
from app.services.user_card_progress_service import UserCardProgressService

TAG = "progress"
TAG_METADATA = {
    "name": TAG,
    "description": "학습 진행 관련 API. FSRS 알고리즘 기반의 카드 복습, 복습 예정 카드 조회, 학습 진도 관리를 처리합니다.",
}

router = APIRouter(prefix="/progress", tags=[TAG])


@router.post(
    "/review",
    response_model=UserCardProgressRead,
    summary="카드 복습 결과 제출",
    description="카드 복습 결과를 제출하고 FSRS 알고리즘으로 다음 복습 일정을 계산합니다.",
    responses={
        200: {"description": "복습 결과 처리 성공. 업데이트된 학습 진행 정보 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "카드를 찾을 수 없음"},
        422: {"description": "유효성 검사 실패 - 필수 필드 누락"},
    },
)
async def submit_card_review(
    review_data: ReviewRequest,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    카드 복습 결과를 제출합니다.

    **인증 필요:** Bearer 토큰

    **FSRS 알고리즘 적용:**
    - `is_correct: true` → FSRS "Good" 등급으로 처리 (기억함)
    - `is_correct: false` → FSRS "Again" 등급으로 처리 (잊음)

    **처리 과정:**
    1. 복습 결과를 FSRS 알고리즘에 입력
    2. 다음 복습 날짜 계산 (stability, difficulty 기반)
    3. 학습 진행 통계 업데이트 (정확도, 복습 횟수 등)

    **반환 정보:**
    - 업데이트된 카드 상태 (NEW/LEARNING/REVIEW/RELEARNING)
    - 다음 복습 예정일
    - 누적 정확도 및 복습 통계
    """
    progress = await UserCardProgressService.process_review(
        session, current_user.id, review_data.card_id, review_data.is_correct
    )
    return progress


@router.get(
    "/due",
    response_model=list[UserCardProgressRead],
    summary="복습 예정 카드 조회",
    description="오늘 복습해야 할 카드 목록을 반환합니다.",
    responses={
        200: {"description": "복습 예정 카드 목록 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_due_cards(
    limit: int = Query(default=20, ge=1, le=100, description="반환할 최대 카드 수 (1~100)"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    복습 예정 카드를 조회합니다.

    **인증 필요:** Bearer 토큰

    **조회 기준:**
    - `next_review_date`가 현재 시간 이전인 카드
    - 사용자가 선택한 덱의 카드만 포함
    - 복습 우선순위에 따라 정렬

    **쿼리 파라미터:**
    - `limit`: 반환할 최대 카드 수 (기본값: 20, 최대: 100)
    """
    cards = await UserCardProgressService.get_due_cards(session, current_user.id, limit=limit)
    return cards


@router.get(
    "/new-cards-count",
    response_model=NewCardsCountRead,
    summary="신규/복습 카드 수 조회",
    description="학습 가능한 신규 카드와 복습 예정 카드 수를 반환합니다.",
    responses={
        200: {"description": "카드 수 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_new_cards_count(
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    신규 카드와 복습 예정 카드 수를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `new_cards_count`: 아직 학습하지 않은 신규 카드 수
    - `review_cards_count`: 오늘 복습해야 할 카드 수

    **계산 기준:**
    - 사용자가 선택한 덱 기준
    - `select_all_decks: true`인 경우 모든 공개 덱 포함
    """
    count_data = await UserCardProgressService.get_new_cards_count(session, current_user.id)
    return NewCardsCountRead(**count_data)


@router.get(
    "/{card_id}",
    response_model=UserCardProgressRead,
    summary="특정 카드 학습 진행 조회",
    description="특정 카드에 대한 사용자의 학습 진행 상황을 조회합니다.",
    responses={
        200: {"description": "학습 진행 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "해당 카드의 학습 진행 기록을 찾을 수 없음"},
    },
)
async def get_card_progress(
    card_id: int = Path(description="조회할 카드의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    특정 카드의 학습 진행 상황을 조회합니다.

    **인증 필요:** Bearer 토큰

    **파라미터:**
    - `card_id`: 조회할 카드의 ID

    **반환 정보:**
    - FSRS 파라미터: stability, difficulty, interval
    - 카드 상태: NEW, LEARNING, REVIEW, RELEARNING
    - 통계: 총 복습 횟수, 정확도, 연속 정답 수
    - 일정: 다음 복습일, 마지막 복습일
    """
    progress = await UserCardProgressService.get_user_card_progress(
        session, current_user.id, card_id
    )
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this card",
        )
    return progress
