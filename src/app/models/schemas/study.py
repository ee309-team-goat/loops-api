"""Schemas for study session endpoints."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class SessionCompleteRequest(SQLModel):
    """Schema for completing a study session."""

    cards_studied: int = Field(ge=0, description="Total cards studied in session")
    cards_correct: int = Field(ge=0, description="Number of correct answers")
    duration_seconds: int = Field(ge=0, description="Session duration in seconds")


class SessionSummary(SQLModel):
    """Summary of a completed study session."""

    total_cards: int
    correct: int
    wrong: int
    accuracy: float
    duration_seconds: int


class StreakInfo(SQLModel):
    """Streak information after session completion."""

    current_streak: int
    longest_streak: int
    is_new_record: bool
    streak_status: str  # "continued" | "started" | "broken"
    message: str


class DailyGoalStatus(SQLModel):
    """Daily goal status after session completion."""

    goal: int
    completed: int
    progress: float
    is_completed: bool


class SessionCompleteResponse(SQLModel):
    """Response after completing a study session."""

    session_summary: SessionSummary
    streak: StreakInfo
    daily_goal: DailyGoalStatus


class SessionStartRequest(SQLModel):
    """Schema for starting a study session."""

    new_cards_limit: int = Field(default=10, ge=0, le=50, description="Max new cards to include")
    review_cards_limit: int = Field(
        default=20, ge=0, le=100, description="Max review cards to include"
    )


class SessionCard(SQLModel):
    """Card information for a study session."""

    id: int
    english_word: str
    korean_meaning: str
    part_of_speech: str | None = None
    pronunciation_ipa: str | None = None
    definition_en: str | None = None
    example_sentences: list | None = None
    is_new: bool  # True if user hasn't studied this card before


class SessionStartResponse(SQLModel):
    """Response when starting a study session."""

    session_id: str  # UUID for tracking
    total_cards: int
    new_cards_count: int
    review_cards_count: int
    cards: list[SessionCard]
    started_at: datetime
