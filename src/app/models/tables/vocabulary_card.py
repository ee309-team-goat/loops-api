from typing import Any, Optional

from sqlmodel import Column, Field, JSON, SQLModel

from app.models.base import TimestampMixin


class VocabularyCardBase(SQLModel):
    """Base VocabularyCard model with shared fields."""

    english_word: str = Field(max_length=255, index=True)
    korean_meaning: str = Field(max_length=255)
    part_of_speech: Optional[str] = Field(default=None, max_length=50)  # noun, verb, adjective, etc.

    # Pronunciation
    pronunciation_ipa: Optional[str] = Field(default=None, max_length=255)  # /ˈkɒntrækt/

    # Definition
    definition_en: Optional[str] = Field(default=None)  # English definition

    # Categorization
    difficulty_level: Optional[str] = Field(default=None, max_length=50, index=True)  # beginner, intermediate, advanced
    cefr_level: Optional[str] = Field(default=None, max_length=10)  # A1-C2
    category: Optional[str] = Field(default=None, max_length=50)  # DB-6: e.g., "business", "travel", "academic"

    # Word frequency and selection (DB-5)
    frequency_rank: Optional[int] = Field(default=None, index=True)  # Lower rank = more common word (1=most common)

    # Audio (DB-9)
    audio_url: Optional[str] = Field(default=None, max_length=500)  # Path or URL to pronunciation audio

    # Deck Organization
    deck_id: Optional[int] = Field(default=None, foreign_key="decks.id", index=True)

    # Metadata
    is_verified: bool = Field(default=False)  # Verified card status


class VocabularyCard(VocabularyCardBase, TimestampMixin, table=True):
    """VocabularyCard database model."""

    __tablename__ = "vocabulary_cards"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

    # JSONB fields for complex data
    # Format: [{"en": "...", "ko": "...", "context": "business"}, ...]
    example_sentences: Optional[dict[str, Any] | list[Any]] = Field(default=None, sa_column=Column(JSON))

    # Format: ["business", "IT", "TOEIC"]
    tags: Optional[dict[str, Any] | list[Any]] = Field(default=None, sa_column=Column(JSON))
