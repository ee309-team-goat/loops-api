from typing import Any, Optional

from sqlmodel import Field, SQLModel

from app.models.tables.vocabulary_card import VocabularyCardBase


class VocabularyCardCreate(VocabularyCardBase):
    """Schema for creating a vocabulary card."""

    example_sentences: Optional[list[dict[str, str]]] = None
    tags: Optional[list[str]] = None


class VocabularyCardRead(VocabularyCardBase):
    """Schema for reading a vocabulary card."""

    id: int
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
    tags: Optional[list[str]] = None
    deck_id: Optional[int] = None
    is_verified: Optional[bool] = None
