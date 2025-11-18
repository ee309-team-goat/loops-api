from datetime import datetime
from typing import Any, Optional

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


class DeckBase(SQLModel):
    """Base Deck model with shared fields."""

    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=100, index=True)  # business/toeic/academic/daily
    difficulty_level: Optional[str] = Field(default=None, max_length=50)  # beginner/intermediate/advanced
    is_public: bool = Field(default=False, index=True)
    is_official: bool = Field(default=False)


class Deck(DeckBase, TimestampMixin, table=True):
    """Deck database model."""

    __tablename__ = "decks"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    creator_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    card_count: int = Field(default=0)
    learning_count: int = Field(default=0)


class DeckCreate(DeckBase):
    """Schema for creating a deck."""

    pass


class DeckRead(DeckBase):
    """Schema for reading a deck."""

    id: int
    creator_id: Optional[int] = None
    card_count: int
    learning_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class DeckUpdate(SQLModel):
    """Schema for updating a deck."""

    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=100)
    difficulty_level: Optional[str] = Field(default=None, max_length=50)
    is_public: Optional[bool] = None
    is_official: Optional[bool] = None
