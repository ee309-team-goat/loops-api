from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint

from app.models.base import TimestampMixin


class UserDeckBase(SQLModel):
    """Base UserDeck model with shared fields."""

    user_id: int = Field(foreign_key="users.id", index=True)
    deck_id: int = Field(foreign_key="decks.id", index=True)
    is_active: bool = Field(default=True)


class UserDeck(UserDeckBase, TimestampMixin, table=True):
    """UserDeck database model for user-deck relationships."""

    __tablename__ = "user_decks"
    __table_args__ = (UniqueConstraint("user_id", "deck_id", name="idx_user_decks_user_deck"),)

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_studied_at: Optional[datetime] = Field(default=None)


class UserDeckCreate(UserDeckBase):
    """Schema for creating a user-deck relationship."""

    pass


class UserDeckRead(UserDeckBase):
    """Schema for reading a user-deck relationship."""

    id: int
    started_at: datetime
    last_studied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserDeckUpdate(SQLModel):
    """Schema for updating a user-deck relationship."""

    is_active: Optional[bool] = None
    last_studied_at: Optional[datetime] = None
