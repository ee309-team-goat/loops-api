from datetime import datetime
from typing import Optional

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
    def difficulty_level_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validate difficulty level."""
        if v is None:
            return v
        allowed_levels = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed_levels:
            raise ValueError(
                f"Difficulty level must be one of: {', '.join(allowed_levels)}"
            )
        return v


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

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate name is not empty."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Deck name cannot be empty or whitespace")
        return v.strip()

    @field_validator("difficulty_level")
    @classmethod
    def difficulty_level_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validate difficulty level."""
        if v is None:
            return v
        allowed_levels = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed_levels:
            raise ValueError(
                f"Difficulty level must be one of: {', '.join(allowed_levels)}"
            )
        return v
