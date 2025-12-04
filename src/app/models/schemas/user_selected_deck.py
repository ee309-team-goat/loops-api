"""Schemas for UserSelectedDeck model."""

from datetime import datetime

from sqlmodel import SQLModel


class UserSelectedDeckCreate(SQLModel):
    """Schema for creating a user selected deck."""

    user_id: int
    deck_id: int


class UserSelectedDeckRead(SQLModel):
    """Schema for reading a user selected deck."""

    id: int
    user_id: int
    deck_id: int
    created_at: datetime
    updated_at: datetime | None = None
