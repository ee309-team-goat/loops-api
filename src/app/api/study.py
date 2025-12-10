"""
학습 세션 관련 API 엔드포인트.

학습 세션 시작/완료, 스트릭 업데이트, 일일 목표 진행 상황을 관리합니다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import (
    SessionCompleteRequest,
    SessionCompleteResponse,
    SessionStartRequest,
    SessionStartResponse,
)
from app.services.study_session_service import StudySessionService

TAG = "study"
TAG_METADATA = {
    "name": TAG,
    "description": "학습 세션 관련 API. 학습 세션 시작/완료, 스트릭 업데이트, 일일 목표 진행 상황을 관리합니다.",
}

router = APIRouter(prefix="/study", tags=[TAG])


@router.post(
    "/session/complete",
    response_model=SessionCompleteResponse,
    summary="학습 세션 완료",
    description="학습 세션을 완료하고 사용자 통계를 업데이트합니다.",
    responses={
        200: {"description": "세션 완료 처리 성공. 세션 요약, 스트릭, 일일 목표 상태 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 필수 필드 누락 또는 형식 오류"},
    },
)
async def complete_study_session(
    request: SessionCompleteRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> SessionCompleteResponse:
    """
    학습 세션을 완료합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `cards_studied`: 학습한 총 카드 수
    - `cards_correct`: 정답 수
    - `duration_seconds`: 학습 시간 (초)

    **처리 내용:**
    1. 세션 결과 저장
    2. 스트릭 업데이트 (연속 학습일)
    3. 총 학습 시간 누적
    4. 일일 목표 진행 상황 업데이트

    **반환 정보:**
    - `session_summary`: 세션 결과 요약 (총 카드, 정답, 오답, 정확도, 시간)
    - `streak`: 스트릭 정보 (현재/최장 스트릭, 신기록 여부, 상태, 메시지)
    - `daily_goal`: 일일 목표 상태 (목표, 완료, 진행률, 달성 여부)
    """
    return await StudySessionService.complete_session(
        session=session,
        profile=current_profile,
        cards_studied=request.cards_studied,
        cards_correct=request.cards_correct,
        duration_seconds=request.duration_seconds,
    )


@router.post(
    "/session/start",
    response_model=SessionStartResponse,
    summary="학습 세션 시작",
    description="새로운 학습 세션을 시작하고 학습할 카드 목록을 반환합니다.",
    responses={
        200: {"description": "세션 시작 성공. 학습할 카드 목록 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 파라미터 값"},
    },
)
async def start_study_session(
    request: SessionStartRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> SessionStartResponse:
    """
    새로운 학습 세션을 시작합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `new_cards_limit`: 신규 카드 최대 수 (기본값: 10, 최대: 50)
    - `review_cards_limit`: 복습 카드 최대 수 (기본값: 20, 최대: 100)

    **카드 구성:**
    - 신규 카드: 사용 빈도순으로 정렬하여 제공
    - 복습 카드: 복습 예정일이 지난 카드 우선

    **반환 정보:**
    - `session_id`: 세션 식별용 UUID
    - `total_cards`: 총 카드 수
    - `new_cards_count`: 신규 카드 수
    - `review_cards_count`: 복습 카드 수
    - `cards`: 학습할 카드 목록 (영어 단어, 뜻, 발음, 예문 포함)
    - `started_at`: 세션 시작 시간

    **카드 정보:**
    - `is_new: true` → 처음 학습하는 카드
    - `is_new: false` → 복습 카드
    """
    return await StudySessionService.start_session(
        session=session,
        user_id=current_profile.id,
        new_cards_limit=request.new_cards_limit,
        review_cards_limit=request.review_cards_limit,
    )
