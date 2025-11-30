"""UserSelectedDeck model for tracking user's selected decks."""

from typing import Optional

from sqlmodel import Field, UniqueConstraint

from app.models.base import TimestampMixin


class UserSelectedDeck(TimestampMixin, table=True):
    """Junction table for user's selected decks.
    
    Tracks which decks a user has selected for learning.
    Only used when user.select_all_decks is False.
    """

    __tablename__ = "user_selected_decks"
    __table_args__ = (UniqueConstraint("user_id", "deck_id", name="uq_user_deck"),)

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    deck_id: int = Field(foreign_key="decks.id", index=True, nullable=False)

