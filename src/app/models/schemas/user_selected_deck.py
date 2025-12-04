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


class SelectDecksRequest(SQLModel):
    """Schema for selecting decks."""

    select_all: bool
    deck_ids: list[int] | None = None


class SelectDecksResponse(SQLModel):
    """Schema for selected decks response."""

    select_all: bool
    selected_deck_ids: list[int]


class SelectedDeckInfo(SQLModel):
    """Schema for selected deck information."""

    id: int
    name: str
    total_cards: int
    progress_percent: float


class GetSelectedDecksResponse(SQLModel):
    """Schema for getting selected decks."""

    select_all: bool
    deck_ids: list[int]
    decks: list[SelectedDeckInfo]
