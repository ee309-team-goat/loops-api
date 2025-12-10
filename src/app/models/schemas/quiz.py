"""퀴즈 관련 스키마."""

from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class QuizType(str, Enum):
    """퀴즈 유형."""

    WORD_TO_MEANING = "word_to_meaning"  # 영어 단어 보고 뜻 맞추기
    MEANING_TO_WORD = "meaning_to_word"  # 뜻 보고 영어 단어 맞추기
    CLOZE = "cloze"  # 빈칸 채우기
    LISTENING = "listening"  # 발음 듣고 단어 맞추기


class ClozeQuestion(SQLModel):
    """빈칸 채우기 문제 스키마."""

    sentence: str = Field(
        description="빈칸이 포함된 문장 (예: 'The company signed a _____ with...')"
    )
    answer: str = Field(description="정답 단어 (예: 'contract')")
    hint: str | None = Field(default=None, description="힌트 (예: '계약')")
    audio_url: str | None = Field(default=None, description="듣기 모드용 오디오 URL")


class QuizCard(SQLModel):
    """퀴즈 카드 스키마."""

    card_id: int = Field(description="카드 고유 ID")
    quiz_type: QuizType = Field(description="퀴즈 유형")
    question: str | ClozeQuestion = Field(description="문제 (문자열 또는 ClozeQuestion)")
    answer: str = Field(description="정답")
    options: list[str] | None = Field(default=None, description="4지선다 선택지")
    audio_url: str | None = Field(default=None, description="오디오 URL (듣기 모드용)")
    extra_info: dict | None = Field(default=None, description="추가 정보 (품사, 예문 등)")


class QuizStartRequest(SQLModel):
    """퀴즈 세션 시작 요청 스키마."""

    quiz_type: QuizType = Field(description="퀴즈 유형")
    cards_limit: int = Field(default=10, ge=1, le=50, description="퀴즈 카드 수 (1~50)")
    include_new: bool = Field(default=True, description="새 카드 포함 여부")
    include_review: bool = Field(default=True, description="복습 카드 포함 여부")


class QuizSessionResponse(SQLModel):
    """퀴즈 세션 시작 응답 스키마."""

    session_id: str = Field(description="세션 식별용 UUID")
    quiz_type: QuizType = Field(description="퀴즈 유형")
    total_cards: int = Field(description="총 퀴즈 카드 수")
    cards: list[QuizCard] = Field(description="퀴즈 카드 목록")
    started_at: datetime = Field(description="세션 시작 시간 (UTC)")


class AnswerSubmitRequest(SQLModel):
    """퀴즈 정답 제출 요청 스키마."""

    card_id: int = Field(description="카드 ID")
    answer: str = Field(description="사용자 입력 정답")
    quiz_type: QuizType = Field(description="퀴즈 유형")
    response_time_ms: int | None = Field(default=None, ge=0, description="응답 시간 (밀리초)")


class AnswerResult(SQLModel):
    """퀴즈 정답 제출 결과 스키마."""

    card_id: int = Field(description="카드 ID")
    is_correct: bool = Field(description="정답 여부")
    correct_answer: str = Field(description="정답")
    user_answer: str = Field(description="사용자 입력 답")
    feedback: str | None = Field(default=None, description="피드백 메시지")


class QuizCompleteRequest(SQLModel):
    """퀴즈 완료 요청 스키마."""

    session_id: str = Field(description="세션 ID")
    total_answered: int = Field(ge=0, description="답변한 총 문제 수")
    correct_count: int = Field(ge=0, description="정답 수")
    duration_seconds: int = Field(ge=0, description="소요 시간 (초)")


class QuizCompleteResponse(SQLModel):
    """퀴즈 완료 응답 스키마."""

    total_answered: int = Field(description="답변한 총 문제 수")
    correct_count: int = Field(description="정답 수")
    accuracy: float = Field(description="정확도 (%)")
    duration_seconds: int = Field(description="소요 시간 (초)")
    xp_earned: int = Field(default=0, description="획득한 경험치")
