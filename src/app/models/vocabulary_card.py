from typing import Any, Optional

from sqlmodel import Column, Field, JSON, SQLModel

from app.models.base import TimestampMixin


class VocabularyCardBase(SQLModel):
    """Base VocabularyCard model with shared fields."""

    word: str = Field(max_length=255, index=True)
    translation: str = Field(max_length=255)
    part_of_speech: Optional[str] = Field(default=None, max_length=50)  # noun, verb, adjective, etc.

    # Pronunciation
    pronunciation_ipa: Optional[str] = Field(default=None, max_length=255)  # /kənˈtrækt/
    pronunciation_kr: Optional[str] = Field(default=None, max_length=255)  # 컨트랙트

    # Definitions
    definition_en: Optional[str] = Field(default=None)  # English definition

    # Media URLs
    audio_url: Optional[str] = Field(default=None, max_length=500)
    image_url: Optional[str] = Field(default=None, max_length=500)

    # Categorization
    difficulty_level: Optional[str] = Field(default=None, max_length=50, index=True)  # beginner, intermediate, advanced
    frequency_rank: Optional[int] = Field(default=None, index=True)  # Word frequency ranking (lower = more common)
    cefr_level: Optional[str] = Field(default=None, max_length=10)  # A1-C2

    # Deck Organization
    deck_id: Optional[int] = Field(default=None, foreign_key="decks.id", index=True)

    # Metadata
    source: Optional[str] = Field(default=None, max_length=255)
    usage_notes: Optional[str] = Field(default=None)  # AI-generated usage notes
    etymology: Optional[str] = Field(default=None)  # Word etymology
    is_verified: bool = Field(default=False)  # Verified card status


class VocabularyCard(VocabularyCardBase, TimestampMixin, table=True):
    """VocabularyCard database model."""

    __tablename__ = "vocabulary_cards"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

    # JSONB fields for complex data
    # Format: ["word1", "word2", ...]
    synonyms: Optional[dict[str, Any] | list[Any]] = Field(default=None, sa_column=Column(JSON))
    antonyms: Optional[dict[str, Any] | list[Any]] = Field(default=None, sa_column=Column(JSON))

    # Format: [{"en": "...", "kr": "...", "context": "business"}, ...]
    example_sentences: Optional[dict[str, Any] | list[Any]] = Field(default=None, sa_column=Column(JSON))

    # Format: ["word combination 1", "word combination 2", ...]
    collocations: Optional[dict[str, Any] | list[Any]] = Field(default=None, sa_column=Column(JSON))

    # Format: ["business", "IT", "TOEIC"]
    tags: Optional[dict[str, Any] | list[Any]] = Field(default=None, sa_column=Column(JSON))


class VocabularyCardCreate(VocabularyCardBase):
    """Schema for creating a vocabulary card."""

    synonyms: Optional[list[str]] = None
    antonyms: Optional[list[str]] = None
    example_sentences: Optional[list[dict[str, str]]] = None
    collocations: Optional[list[str]] = None
    tags: Optional[list[str]] = None


class VocabularyCardRead(VocabularyCardBase):
    """Schema for reading a vocabulary card."""

    id: int
    synonyms: Optional[list[str]] = None
    antonyms: Optional[list[str]] = None
    example_sentences: Optional[list[dict[str, str]]] = None
    collocations: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    created_at: Any  # datetime
    updated_at: Optional[Any] = None  # datetime


class VocabularyCardUpdate(SQLModel):
    """Schema for updating a vocabulary card."""

    word: Optional[str] = Field(default=None, max_length=255)
    translation: Optional[str] = Field(default=None, max_length=255)
    part_of_speech: Optional[str] = Field(default=None, max_length=50)
    pronunciation_ipa: Optional[str] = Field(default=None, max_length=255)
    pronunciation_kr: Optional[str] = Field(default=None, max_length=255)
    definition_en: Optional[str] = None
    synonyms: Optional[list[str]] = None
    antonyms: Optional[list[str]] = None
    example_sentences: Optional[list[dict[str, str]]] = None
    collocations: Optional[list[str]] = None
    audio_url: Optional[str] = Field(default=None, max_length=500)
    image_url: Optional[str] = Field(default=None, max_length=500)
    difficulty_level: Optional[str] = Field(default=None, max_length=50)
    frequency_rank: Optional[int] = None
    cefr_level: Optional[str] = Field(default=None, max_length=10)
    tags: Optional[list[str]] = None
    deck_id: Optional[int] = None
    source: Optional[str] = Field(default=None, max_length=255)
    usage_notes: Optional[str] = None
    etymology: Optional[str] = None
    is_verified: Optional[bool] = None
