from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AIInteractionBase(SQLModel):
    """Base AIInteraction model with shared fields."""

    user_id: int = Field(foreign_key="users.id", index=True)
    card_id: Optional[int] = Field(default=None, foreign_key="vocabulary_cards.id", index=True)
    interaction_type: str = Field(max_length=50, index=True)  # example_generation/pronunciation_check/explanation
    user_input: Optional[str] = Field(default=None)
    ai_response: Optional[str] = Field(default=None)
    model_used: Optional[str] = Field(default=None, max_length=100)  # gpt-4/claude-3.5/etc
    tokens_used: Optional[int] = Field(default=None)
    response_time_ms: Optional[int] = Field(default=None)
    feedback_rating: Optional[int] = Field(default=None)  # 1-5


class AIInteraction(AIInteractionBase, table=True):
    """AIInteraction database model for logging AI interactions."""

    __tablename__ = "ai_interactions"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class AIInteractionCreate(AIInteractionBase):
    """Schema for creating an AI interaction."""

    pass


class AIInteractionRead(AIInteractionBase):
    """Schema for reading an AI interaction."""

    id: int
    created_at: datetime


class AIInteractionUpdate(SQLModel):
    """Schema for updating an AI interaction."""

    feedback_rating: Optional[int] = Field(default=None, ge=1, le=5)
