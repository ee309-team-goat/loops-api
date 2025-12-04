from typing import Any

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.vocabulary_card import VocabularyCardBase


class VocabularyCardCreate(VocabularyCardBase):
    """Schema for creating a vocabulary card."""

    example_sentences: list[dict[str, str]] | None = None
    tags: list[str] | None = None

    @field_validator("english_word", "korean_meaning")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("cefr_level")
    @classmethod
    def cefr_level_valid(cls, v: str | None) -> str | None:
        """Validate CEFR level is valid."""
        if v is None:
            return v
        allowed_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
        v = v.upper().strip()
        if v not in allowed_levels:
            raise ValueError(f"CEFR level must be one of: {', '.join(allowed_levels)}")
        return v

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

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: list[str] | None) -> list[str] | None:
        """Validate tags are not empty strings."""
        if v is None:
            return v
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]
        return cleaned if cleaned else None


class VocabularyCardRead(VocabularyCardBase):
    """Schema for reading a vocabulary card."""

    id: int
    category: str | None = None
    frequency_rank: int | None = None
    audio_url: str | None = None
    example_sentences: list[dict[str, str]] | None = None
    tags: list[str] | None = None
    created_at: Any  # datetime
    updated_at: Any | None = None  # datetime


class VocabularyCardUpdate(SQLModel):
    """Schema for updating a vocabulary card."""

    english_word: str | None = Field(default=None, max_length=255)
    korean_meaning: str | None = Field(default=None, max_length=255)
    part_of_speech: str | None = Field(default=None, max_length=50)
    pronunciation_ipa: str | None = Field(default=None, max_length=255)
    definition_en: str | None = None
    example_sentences: list[dict[str, str]] | None = None
    difficulty_level: str | None = Field(default=None, max_length=50)
    cefr_level: str | None = Field(default=None, max_length=10)
    category: str | None = Field(default=None, max_length=50)
    frequency_rank: int | None = Field(default=None, ge=0)
    audio_url: str | None = Field(default=None, max_length=500)
    tags: list[str] | None = None
    deck_id: int | None = Field(default=None, gt=0)
    is_verified: bool | None = None

    @field_validator("english_word", "korean_meaning")
    @classmethod
    def not_empty(cls, v: str | None) -> str | None:
        """Validate string fields are not empty."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("cefr_level")
    @classmethod
    def cefr_level_valid(cls, v: str | None) -> str | None:
        """Validate CEFR level is valid."""
        if v is None:
            return v
        allowed_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
        v = v.upper().strip()
        if v not in allowed_levels:
            raise ValueError(f"CEFR level must be one of: {', '.join(allowed_levels)}")
        return v

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

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: list[str] | None) -> list[str] | None:
        """Validate tags are not empty strings."""
        if v is None:
            return v
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]
        return cleaned if cleaned else None
