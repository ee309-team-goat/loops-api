"""Schemas for UserSelectedDeck model."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


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
    updated_at: Optional[datetime] = None


class SelectDecksRequest(SQLModel):
    """Schema for selecting decks."""

    select_all: bool
    deck_ids: Optional[list[int]] = None


class SelectDecksResponse(SQLModel):
    """Schema for selected decks response."""

    select_all: bool
    selected_deck_ids: list[int]

