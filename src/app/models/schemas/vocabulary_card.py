from typing import Any, Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.vocabulary_card import VocabularyCardBase


class VocabularyCardCreate(VocabularyCardBase):
    """Schema for creating a vocabulary card."""

    example_sentences: Optional[list[dict[str, str]]] = None
    tags: Optional[list[str]] = None

    @field_validator("english_word", "korean_meaning")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Validate required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("cefr_level")
    @classmethod
    def cefr_level_valid(cls, v: Optional[str]) -> Optional[str]:
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

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate tags are not empty strings."""
        if v is None:
            return v
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]
        return cleaned if cleaned else None


class VocabularyCardRead(VocabularyCardBase):
    """Schema for reading a vocabulary card."""

    id: int
    category: Optional[str] = None
    frequency_rank: Optional[int] = None
    audio_url: Optional[str] = None
    example_sentences: Optional[list[dict[str, str]]] = None
    tags: Optional[list[str]] = None
    created_at: Any  # datetime
    updated_at: Optional[Any] = None  # datetime


class VocabularyCardUpdate(SQLModel):
    """Schema for updating a vocabulary card."""

    english_word: Optional[str] = Field(default=None, max_length=255)
    korean_meaning: Optional[str] = Field(default=None, max_length=255)
    part_of_speech: Optional[str] = Field(default=None, max_length=50)
    pronunciation_ipa: Optional[str] = Field(default=None, max_length=255)
    definition_en: Optional[str] = None
    example_sentences: Optional[list[dict[str, str]]] = None
    difficulty_level: Optional[str] = Field(default=None, max_length=50)
    cefr_level: Optional[str] = Field(default=None, max_length=10)
    category: Optional[str] = Field(default=None, max_length=50)
    frequency_rank: Optional[int] = Field(default=None, ge=0)
    audio_url: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[list[str]] = None
    deck_id: Optional[int] = Field(default=None, gt=0)
    is_verified: Optional[bool] = None

    @field_validator("english_word", "korean_meaning")
    @classmethod
    def not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate string fields are not empty."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("cefr_level")
    @classmethod
    def cefr_level_valid(cls, v: Optional[str]) -> Optional[str]:
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

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate tags are not empty strings."""
        if v is None:
            return v
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]
        return cleaned if cleaned else None
