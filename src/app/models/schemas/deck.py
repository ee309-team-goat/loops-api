from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.deck import DeckBase


class DeckCreate(DeckBase):
    """Schema for creating a deck."""

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or not v.strip():
            raise ValueError("Deck name cannot be empty or whitespace")
        return v.strip()

    @field_validator("difficulty_level")
    @classmethod
    def difficulty_level_valid(cls, v: str | None) -> str | None:
        """Validate difficulty level."""
        if v is None:
            return v
        allowed_levels = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed_levels:
            raise ValueError(f"Difficulty level must be one of: {', '.join(allowed_levels)}")
        return v


class DeckRead(DeckBase):
    """Schema for reading a deck."""

    id: int
    creator_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None


class DeckUpdate(SQLModel):
    """Schema for updating a deck."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=100)
    difficulty_level: str | None = Field(default=None, max_length=50)
    is_public: bool | None = None
    is_official: bool | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        """Validate name is not empty."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Deck name cannot be empty or whitespace")
        return v.strip()

    @field_validator("difficulty_level")
    @classmethod
    def difficulty_level_valid(cls, v: str | None) -> str | None:
        """Validate difficulty level."""
        if v is None:
            return v
        allowed_levels = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed_levels:
            raise ValueError(f"Difficulty level must be one of: {', '.join(allowed_levels)}")
        return v


class DeckWithProgressRead(SQLModel):
    """Schema for reading a deck with progress information."""

    id: int
    name: str
    description: str | None = None
    total_cards: int
    learned_cards: int
    learning_cards: int
    new_cards: int
    progress_percent: float


class DecksListResponse(SQLModel):
    """Schema for deck list response with pagination."""

    decks: list[DeckWithProgressRead]
    total: int
    skip: int
    limit: int


class DeckDetailRead(SQLModel):
    """Schema for reading a deck with full details and progress."""

    # From DeckRead
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    is_public: bool
    is_official: bool
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    # From progress calculation
    total_cards: int
    learned_cards: int
    learning_cards: int
    new_cards: int
    progress_percent: float
