"""
퀴즈 관련 API 엔드포인트.

4가지 퀴즈 모드(word_to_meaning, meaning_to_word, cloze, listening)를 지원합니다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import (
    AnswerResult,
    AnswerSubmitRequest,
    QuizCompleteRequest,
    QuizCompleteResponse,
    QuizSessionResponse,
    QuizStartRequest,
)
from app.services.quiz_service import QuizService

TAG = "quiz"
TAG_METADATA = {
    "name": TAG,
    "description": "퀴즈 관련 API. 4가지 퀴즈 모드(word_to_meaning, meaning_to_word, cloze, listening)를 지원합니다.",
}

router = APIRouter(prefix="/quiz", tags=[TAG])


@router.post(
    "/start",
    response_model=QuizSessionResponse,
    summary="퀴즈 세션 시작",
    description="특정 유형의 퀴즈 세션을 시작합니다.",
    responses={
        200: {"description": "퀴즈 세션 시작 성공. 퀴즈 카드 목록 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 파라미터 값"},
    },
)
async def start_quiz(
    request: QuizStartRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> QuizSessionResponse:
    """
    특정 유형의 퀴즈 세션을 시작합니다.

    **인증 필요:** Bearer 토큰

    **퀴즈 유형 (quiz_type):**
    - `word_to_meaning`: 영어 단어를 보고 뜻 맞추기 (4지선다)
    - `meaning_to_word`: 뜻을 보고 영어 단어 맞추기 (4지선다)
    - `cloze`: 빈칸 채우기 - 예문에서 빈칸에 들어갈 단어 맞추기
    - `listening`: 듣기 - 발음을 듣고 단어 맞추기

    **요청 본문:**
    - `quiz_type`: 퀴즈 유형 (필수)
    - `cards_limit`: 퀴즈 카드 수 (기본값: 10, 최대: 50)
    - `include_new`: 새 카드 포함 여부 (기본값: true)
    - `include_review`: 복습 카드 포함 여부 (기본값: true)

    **반환 정보:**
    - `session_id`: 세션 식별용 UUID
    - `quiz_type`: 퀴즈 유형
    - `total_cards`: 총 퀴즈 카드 수
    - `cards`: 퀴즈 카드 목록
    - `started_at`: 세션 시작 시간 (UTC)

    **퀴즈 카드 구조:**
    - `card_id`: 카드 ID
    - `quiz_type`: 퀴즈 유형
    - `question`: 문제 (문자열 또는 ClozeQuestion 객체)
    - `answer`: 정답
    - `options`: 4지선다 선택지
    - `audio_url`: 오디오 URL (듣기 모드용)
    - `extra_info`: 추가 정보 (품사, 발음 등)

    **Cloze 문제의 question 구조:**
    ```json
    {
        "sentence": "The company signed a _____ with...",
        "answer": "contract",
        "hint": "계약",
        "audio_url": null
    }
    ```
    """
    return await QuizService.start_quiz_session(
        session=session,
        user_id=current_profile.id,
        quiz_type=request.quiz_type,
        cards_limit=request.cards_limit,
        include_new=request.include_new,
        include_review=request.include_review,
    )


@router.post(
    "/answer",
    response_model=AnswerResult,
    summary="퀴즈 정답 제출",
    description="퀴즈 정답을 제출하고 결과를 확인합니다.",
    responses={
        200: {"description": "정답 제출 성공. 채점 결과 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 파라미터 값"},
    },
)
async def submit_answer(
    request: AnswerSubmitRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,  # noqa: ARG001
) -> AnswerResult:
    """
    퀴즈 정답을 제출하고 채점 결과를 받습니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `card_id`: 카드 ID (필수)
    - `answer`: 사용자가 입력한 정답 (필수)
    - `quiz_type`: 퀴즈 유형 (필수)
    - `response_time_ms`: 응답 시간 (밀리초, 선택)

    **반환 정보:**
    - `card_id`: 카드 ID
    - `is_correct`: 정답 여부
    - `correct_answer`: 정답
    - `user_answer`: 사용자가 입력한 답
    - `feedback`: 피드백 메시지

    **참고:**
    - 정답 비교는 대소문자를 구분하지 않습니다.
    - FSRS 알고리즘 업데이트는 별도의 `/progress/review` API를 통해 수행합니다.
    """
    # 카드 정보 조회
    from app.models import VocabularyCard

    card = await session.get(VocabularyCard, request.card_id)
    if not card:
        from app.core.exceptions import NotFoundError

        raise NotFoundError(f"Card with id {request.card_id} not found")

    # 퀴즈 타입에 따른 정답 결정
    from app.models import QuizType

    if request.quiz_type == QuizType.WORD_TO_MEANING:
        correct_answer = card.korean_meaning
    elif request.quiz_type in (
        QuizType.MEANING_TO_WORD,
        QuizType.LISTENING,
        QuizType.CLOZE,
    ):
        correct_answer = card.english_word
    else:
        correct_answer = card.english_word

    return QuizService.check_answer(
        card_id=request.card_id,
        user_answer=request.answer,
        correct_answer=correct_answer,
        quiz_type=request.quiz_type,
    )


@router.post(
    "/complete",
    response_model=QuizCompleteResponse,
    summary="퀴즈 세션 완료",
    description="퀴즈 세션을 완료하고 결과를 저장합니다.",
    responses={
        200: {"description": "퀴즈 완료 처리 성공. 최종 결과 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 파라미터 값"},
    },
)
async def complete_quiz(
    request: QuizCompleteRequest,
    session: Annotated[AsyncSession, Depends(get_session)],  # noqa: ARG001
    current_profile: CurrentActiveProfile,  # noqa: ARG001
) -> QuizCompleteResponse:
    """
    퀴즈 세션을 완료합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `session_id`: 세션 ID (필수)
    - `total_answered`: 답변한 총 문제 수 (필수)
    - `correct_count`: 정답 수 (필수)
    - `duration_seconds`: 소요 시간 (초, 필수)

    **반환 정보:**
    - `total_answered`: 답변한 총 문제 수
    - `correct_count`: 정답 수
    - `accuracy`: 정확도 (%)
    - `duration_seconds`: 소요 시간 (초)
    - `xp_earned`: 획득한 경험치

    **참고:**
    - 경험치 계산: 정답 수 × 10 + 보너스 (정확도 80% 이상 시 추가 50)
    - 스트릭 및 학습 통계 업데이트는 `/study/session/complete` API를 통해 수행하세요.
    """
    # 정확도 계산
    accuracy = (
        (request.correct_count / request.total_answered * 100)
        if request.total_answered > 0
        else 0.0
    )

    # 경험치 계산 (정답당 10XP + 80% 이상 시 보너스 50XP)
    base_xp = request.correct_count * 10
    bonus_xp = 50 if accuracy >= 80.0 else 0
    xp_earned = base_xp + bonus_xp

    return QuizCompleteResponse(
        total_answered=request.total_answered,
        correct_count=request.correct_count,
        accuracy=round(accuracy, 1),
        duration_seconds=request.duration_seconds,
        xp_earned=xp_earned,
    )
