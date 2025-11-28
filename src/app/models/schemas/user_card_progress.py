from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel

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
    last_review_date: Optional[datetime] = None
    card_state: CardState
    created_at: datetime
    updated_at: Optional[datetime] = None


class ReviewRequest(SQLModel):
    """Schema for submitting a card review."""

    card_id: int
    is_correct: bool
