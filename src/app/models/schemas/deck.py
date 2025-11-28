from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.tables.deck import DeckBase


class DeckCreate(DeckBase):
    """Schema for creating a deck."""

    pass


class DeckRead(DeckBase):
    """Schema for reading a deck."""

    id: int
    creator_id: Optional[int] = None
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
