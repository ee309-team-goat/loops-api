"""학습 세션 관련 스키마."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class SessionCompleteRequest(SQLModel):
    """학습 세션 완료 요청 스키마."""

    cards_studied: int = Field(ge=0, description="세션에서 학습한 총 카드 수")
    cards_correct: int = Field(ge=0, description="정답으로 처리한 카드 수")
    duration_seconds: int = Field(ge=0, description="학습 시간 (초)")


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


class SessionCompleteResponse(SQLModel):
    """학습 세션 완료 응답 스키마."""

    session_summary: SessionSummary = Field(description="이번 세션 결과 요약")
    streak: StreakInfo = Field(description="스트릭 정보 (연속 학습일)")
    daily_goal: DailyGoalStatus = Field(description="일일 목표 달성 상태")


class SessionStartRequest(SQLModel):
    """학습 세션 시작 요청 스키마."""

    new_cards_limit: int = Field(
        default=10, ge=0, le=50, description="포함할 최대 신규 카드 수 (0~50)"
    )
    review_cards_limit: int = Field(
        default=20, ge=0, le=100, description="포함할 최대 복습 카드 수 (0~100)"
    )


class SessionCard(SQLModel):
    """학습 세션용 카드 정보 스키마."""

    id: int = Field(description="카드 고유 ID")
    english_word: str = Field(description="영어 단어")
    korean_meaning: str = Field(description="한국어 뜻")
    part_of_speech: str | None = Field(default=None, description="품사 (noun, verb 등)")
    pronunciation_ipa: str | None = Field(default=None, description="IPA 발음 기호")
    definition_en: str | None = Field(default=None, description="영어 정의")
    example_sentences: list | None = Field(
        default=None, description="예문 목록 [{sentence, translation}]"
    )
    is_new: bool = Field(description="신규 카드 여부. true=처음 학습, false=복습 카드")


class SessionStartResponse(SQLModel):
    """학습 세션 시작 응답 스키마."""

    session_id: str = Field(description="세션 식별용 UUID. 세션 완료 시 사용")
    total_cards: int = Field(description="이 세션에 포함된 총 카드 수")
    new_cards_count: int = Field(description="신규 카드 수")
    review_cards_count: int = Field(description="복습 카드 수")
    cards: list[SessionCard] = Field(description="학습할 카드 목록")
    started_at: datetime = Field(description="세션 시작 시간 (UTC)")
