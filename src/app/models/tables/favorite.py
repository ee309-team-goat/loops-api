"""Favorite model for user's favorite vocabulary cards."""

from sqlmodel import Field, UniqueConstraint

from app.models.base import TimestampMixin


class Favorite(TimestampMixin, table=True):
    """User's favorite vocabulary cards.

    Allows users to bookmark/favorite cards for quick access.
    """

    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "card_id", name="uq_user_card_favorite"),)

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    card_id: int = Field(foreign_key="vocabulary_cards.id", index=True, nullable=False)
