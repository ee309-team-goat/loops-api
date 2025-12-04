from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.enums import CardState
from app.models.tables.user_card_progress import UserCardProgressBase


class UserCardProgressCreate(UserCardProgressBase):
    """Schema for creating user card progress."""

    next_review_date: datetime
    card_state: CardState = CardState.NEW


class UserCardProgressRead(UserCardProgressBase):
    """Schema for reading user card progress."""

    id: int
    next_review_date: datetime
    last_review_date: datetime | None = None
    card_state: CardState
    created_at: datetime
    updated_at: datetime | None = None


class ReviewRequest(SQLModel):
    """Schema for submitting a card review."""

    card_id: int = Field(gt=0, description="Card ID must be positive")
    is_correct: bool


class TodayProgressRead(SQLModel):
    """Schema for reading today's learning progress statistics."""

    total_reviews: int
    correct_count: int
    wrong_count: int
    accuracy_rate: float
    daily_goal: int
    goal_progress: float


class NewCardsCountRead(SQLModel):
    """Schema for reading new and review cards count."""

    new_cards_count: int
    review_cards_count: int
