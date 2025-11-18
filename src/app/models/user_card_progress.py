import enum
from datetime import datetime
from typing import Any, Optional

from sqlmodel import Column, Enum, Field, ForeignKey, JSON, SQLModel, UniqueConstraint

from app.models.base import TimestampMixin


class CardState(str, enum.Enum):
    """Card state enum for FSRS algorithm."""

    NEW = "new"  # New card, never studied
    LEARNING = "learning"  # Currently learning (short intervals)
    REVIEW = "review"  # In review phase (longer intervals)
    RELEARNING = "relearning"  # Failed review, relearning


class UserCardProgressBase(SQLModel):
    """Base UserCardProgress model with shared fields."""

    user_id: int = Field(foreign_key="users.id", index=True)
    card_id: int = Field(foreign_key="vocabulary_cards.id", index=True)

    # FSRS Algorithm Parameters
    easiness_factor: float = Field(default=2.5)  # SM-2 compatibility (deprecated in FSRS)
    interval: int = Field(default=0)  # Days until next review
    repetitions: int = Field(default=0)  # Number of successful reviews

    # Statistics
    total_reviews: int = Field(default=0)
    correct_count: int = Field(default=0)
    wrong_count: int = Field(default=0)
    accuracy_rate: float = Field(default=0.0)
    average_response_time: int = Field(default=0)  # in seconds

    # FSRS Extended Parameters
    stability: Optional[float] = Field(default=0.0)  # Memory stability
    difficulty: Optional[float] = Field(default=5.0)  # Card difficulty (1-10)
    scheduled_days: int = Field(default=0)  # Scheduled interval

    # Additional FSRS fields for py-fsrs compatibility
    lapses: int = Field(default=0)  # Number of times forgotten
    reps_since_lapse: int = Field(default=0)  # Successful reps since last lapse
    elapsed_days: int = Field(default=0)  # Days between reviews


class UserCardProgress(UserCardProgressBase, TimestampMixin, table=True):
    """UserCardProgress database model for tracking FSRS progress."""

    __tablename__ = "user_card_progress"
    __table_args__ = (UniqueConstraint("user_id", "card_id", name="uq_user_card"),)

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

    # Review Scheduling
    next_review_date: datetime = Field(index=True)
    last_review_date: Optional[datetime] = Field(default=None)

    # Card State
    card_state: CardState = Field(
        default=CardState.NEW, sa_column=Column(Enum(CardState), nullable=False, index=True)
    )

    # Milestone Dates
    first_studied_at: Optional[datetime] = Field(default=None)
    mastered_at: Optional[datetime] = Field(default=None)

    # Quality History (JSONB)
    # Format: [{"date": "2024-01-01T10:00:00Z", "quality": 3, "interval": 1, "stability": 2.5, "difficulty": 5.0}, ...]
    quality_history: Optional[dict[str, Any] | list[Any]] = Field(default=None, sa_column=Column(JSON))


class UserCardProgressCreate(UserCardProgressBase):
    """Schema for creating user card progress."""

    next_review_date: datetime
    card_state: CardState = CardState.NEW
    quality_history: Optional[list[dict[str, Any]]] = None


class UserCardProgressRead(UserCardProgressBase):
    """Schema for reading user card progress."""

    id: int
    next_review_date: datetime
    last_review_date: Optional[datetime] = None
    card_state: CardState
    quality_history: Optional[list[dict[str, Any]]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserCardProgressUpdate(SQLModel):
    """Schema for updating user card progress."""

    easiness_factor: Optional[float] = None
    interval: Optional[int] = None
    repetitions: Optional[int] = None
    next_review_date: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    total_reviews: Optional[int] = None
    correct_count: Optional[int] = None
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    lapses: Optional[int] = None
    elapsed_days: Optional[int] = None
    card_state: Optional[CardState] = None
    quality_history: Optional[list[dict[str, Any]]] = None


class ReviewRequest(SQLModel):
    """Schema for submitting a card review."""

    card_id: int
    rating: int = Field(ge=1, le=4)  # 1=Again, 2=Hard, 3=Good, 4=Easy


class ReviewResponse(SQLModel):
    """Schema for review response with scheduling info."""

    progress: UserCardProgressRead
    next_review_date: datetime
    interval_days: int
    card_state: CardState
