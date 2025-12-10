"""학습 세션 관련 스키마."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.enums import CardState, QuizType


class ClozeQuestion(SQLModel):
    """빈칸 채우기 문제 스키마."""

    sentence: str = Field(
        description="빈칸이 포함된 문장 (예: 'The company signed a _____ with...')"
    )
    answer: str = Field(description="정답 단어 (예: 'contract')")
    hint: str | None = Field(default=None, description="힌트 (예: '계약')")
    audio_url: str | None = Field(default=None, description="듣기 모드용 오디오 URL")


# ============================================================
# Session Start
# ============================================================


class SessionStartRequest(SQLModel):
    """학습 세션 시작 요청 스키마."""

    new_cards_limit: int = Field(
        default=30, ge=0, le=50, description="포함할 최대 신규 카드 수 (0~50)"
    )
    review_cards_limit: int = Field(
        default=30, ge=0, le=100, description="포함할 최대 복습 카드 수 (0~100)"
    )


class SessionStartResponse(SQLModel):
    """학습 세션 시작 응답 스키마."""

    session_id: UUID = Field(description="세션 식별용 UUID")
    total_cards: int = Field(description="이 세션에 포함된 총 카드 수")
    new_cards_count: int = Field(description="신규 카드 수")
    review_cards_count: int = Field(description="복습 카드 수")
    started_at: datetime = Field(description="세션 시작 시간 (UTC)")


# ============================================================
# Card Request/Response
# ============================================================


class CardRequest(SQLModel):
    """다음 카드 요청 스키마."""

    session_id: UUID = Field(description="세션 ID")
    quiz_type: QuizType = Field(description="이 카드에 적용할 퀴즈 유형")


class StudyCard(SQLModel):
    """학습 카드 스키마 (퀴즈 포맷팅 포함)."""

    id: int = Field(description="카드 고유 ID")
    english_word: str = Field(description="영어 단어")
    korean_meaning: str = Field(description="한국어 뜻")
    part_of_speech: str | None = Field(default=None, description="품사 (noun, verb 등)")
    pronunciation_ipa: str | None = Field(default=None, description="IPA 발음 기호")
    definition_en: str | None = Field(default=None, description="영어 정의")
    example_sentences: list | None = Field(
        default=None, description="예문 목록 [{sentence, translation}]"
    )
    audio_url: str | None = Field(default=None, description="오디오 URL")
    is_new: bool = Field(description="신규 카드 여부. true=처음 학습, false=복습 카드")

    # 퀴즈 포맷팅 필드
    quiz_type: QuizType = Field(description="퀴즈 유형")
    question: str | ClozeQuestion = Field(description="문제 (문자열 또는 ClozeQuestion)")
    options: list[str] | None = Field(default=None, description="4지선다 선택지")


class CardResponse(SQLModel):
    """다음 카드 응답 스키마."""

    card: StudyCard | None = Field(description="학습 카드. None이면 모든 카드 완료")
    cards_remaining: int = Field(description="남은 카드 수")
    cards_completed: int = Field(description="완료한 카드 수")


# ============================================================
# Answer Request/Response
# ============================================================


class AnswerRequest(SQLModel):
    """정답 제출 요청 스키마."""

    session_id: UUID = Field(description="세션 ID")
    card_id: int = Field(description="카드 ID")
    answer: str = Field(description="사용자 입력 정답")
    response_time_ms: int | None = Field(default=None, ge=0, description="응답 시간 (밀리초)")


class AnswerResponse(SQLModel):
    """정답 제출 응답 스키마."""

    card_id: int = Field(description="카드 ID")
    is_correct: bool = Field(description="정답 여부")
    correct_answer: str = Field(description="정답")
    user_answer: str = Field(description="사용자 입력 답")
    feedback: str | None = Field(default=None, description="피드백 메시지")

    # FSRS 업데이트 정보
    next_review_date: datetime | None = Field(description="다음 복습 예정일")
    card_state: CardState = Field(description="카드 상태 (NEW/LEARNING/REVIEW/RELEARNING)")


# ============================================================
# Session Complete
# ============================================================


class SessionCompleteRequest(SQLModel):
    """학습 세션 완료 요청 스키마."""

    session_id: UUID = Field(description="세션 ID")


class SessionSummary(SQLModel):
    """학습 세션 결과 요약 스키마."""

    total_cards: int = Field(description="학습한 총 카드 수")
    correct: int = Field(description="정답 수")
    wrong: int = Field(description="오답 수")
    accuracy: float = Field(description="정확도 (%) - (정답/총카드)*100")
    duration_seconds: int = Field(description="학습 시간 (초)")


class StreakInfo(SQLModel):
    """세션 완료 후 스트릭 정보 스키마."""

    current_streak: int = Field(description="현재 연속 학습일 수")
    longest_streak: int = Field(description="최장 연속 학습일 수 (역대 기록)")
    is_new_record: bool = Field(description="이번 세션으로 최장 기록을 갱신했는지 여부")
    streak_status: str = Field(
        description="스트릭 상태. 'continued'(유지), 'started'(새로 시작), 'broken'(끊김 후 재시작)"
    )
    message: str = Field(description="사용자에게 표시할 동기 부여 메시지")


class DailyGoalStatus(SQLModel):
    """세션 완료 후 일일 목표 상태 스키마."""

    goal: int = Field(description="설정된 일일 목표 카드 수")
    completed: int = Field(description="오늘 학습 완료한 총 카드 수 (이 세션 포함)")
    progress: float = Field(description="목표 달성률 (%) - (완료/목표)*100, 최대 100")
    is_completed: bool = Field(description="일일 목표 달성 여부")


class XPInfo(SQLModel):
    """경험치 정보 스키마."""

    base_xp: int = Field(description="기본 경험치 (정답당 10XP)")
    bonus_xp: int = Field(description="보너스 경험치 (80% 이상 시 +50XP)")
    total_xp: int = Field(description="총 획득 경험치")


class SessionCompleteResponse(SQLModel):
    """학습 세션 완료 응답 스키마."""

    session_summary: SessionSummary = Field(description="이번 세션 결과 요약")
    streak: StreakInfo = Field(description="스트릭 정보 (연속 학습일)")
    daily_goal: DailyGoalStatus = Field(description="일일 목표 달성 상태")
    xp: XPInfo = Field(description="획득 경험치 정보")


# ============================================================
# Study Overview
# ============================================================


class DueCardSummary(SQLModel):
    """복습 예정 카드 요약 스키마."""

    card_id: int = Field(description="카드 고유 ID")
    english_word: str = Field(description="영어 단어")
    korean_meaning: str = Field(description="한국어 뜻")
    next_review_date: datetime = Field(description="다음 복습 예정일")
    card_state: CardState = Field(description="카드 상태 (NEW/LEARNING/REVIEW/RELEARNING)")


class StudyOverviewResponse(SQLModel):
    """학습 현황 개요 응답 스키마."""

    new_cards_count: int = Field(description="학습 가능한 신규 카드 수")
    review_cards_count: int = Field(description="복습 예정 카드 수")
    total_available: int = Field(description="총 학습 가능 카드 수")
    due_cards: list[DueCardSummary] = Field(description="복습 예정 카드 목록")
