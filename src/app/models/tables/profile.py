"""Profile model for user app-specific data linked to Supabase Auth."""

from datetime import date
from uuid import UUID

from sqlalchemy import Uuid
from sqlmodel import Column, Field, SQLModel

from app.models.base import TimestampMixin


class ProfileBase(SQLModel):
    """Base Profile model with shared fields."""

    # Learning preferences (DB-1, DB-2)
    select_all_decks: bool = Field(default=True)  # If true, study from all decks
    daily_goal: int = Field(default=20)  # Daily learning goal (number of cards)

    # User settings (DB-8)
    timezone: str = Field(default="UTC", max_length=50)
    theme: str = Field(default="auto", max_length=20)  # light/dark/auto
    notification_enabled: bool = Field(default=True)

    # UI customization (Issue #55)
    highlight_color: str = Field(
        default="#4CAF50", max_length=20, description="Clue 하이라이트 색상 (HEX 코드)"
    )


class Profile(ProfileBase, TimestampMixin, table=True):
    """Profile database model linked to Supabase Auth user."""

    __tablename__ = "profiles"

    # UUID from Supabase auth.users.id - direct reference, no separate supabase_uid needed
    id: UUID = Field(
        sa_column=Column(Uuid, primary_key=True, nullable=False),
        description="User ID from Supabase Auth (auth.users.id)",
    )

    # Streak tracking
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_study_date: date | None = Field(default=None, index=True)

    # Study statistics
    total_study_time_minutes: int = Field(default=0)
