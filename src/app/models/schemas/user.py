from datetime import date, datetime

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.user import UserBase


class UserCreate(SQLModel):
    """Schema for creating a user (used internally with Supabase Auth)."""

    supabase_uid: str = Field(max_length=255)
    email: str = Field(max_length=255)
    username: str = Field(max_length=100)


class UserRead(UserBase):
    """Schema for reading a user."""

    id: int
    current_streak: int
    longest_streak: int
    last_study_date: date | None = None
    select_all_decks: bool
    daily_goal: int
    timezone: str
    theme: str
    notification_enabled: bool
    total_study_time_minutes: int = 0
    created_at: datetime
    updated_at: datetime | None = None


class UserUpdate(SQLModel):
    """Schema for updating a user (profile fields only, auth handled by Supabase)."""

    email: EmailStr | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None
    select_all_decks: bool | None = None
    daily_goal: int | None = Field(default=None, gt=0, le=1000)
    timezone: str | None = Field(default=None, max_length=50)
    theme: str | None = Field(default=None, max_length=20)
    notification_enabled: bool | None = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str | None) -> str | None:
        """Validate username is alphanumeric and not just whitespace."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Username cannot be empty or whitespace")
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @field_validator("theme")
    @classmethod
    def theme_valid(cls, v: str | None) -> str | None:
        """Validate theme is one of the allowed values."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v


class DailyGoalRead(SQLModel):
    """Schema for reading daily goal information."""

    daily_goal: int
    completed_today: int


class UserLogin(SQLModel):
    """Schema for user login."""

    username: str = Field(max_length=100)
    password: str = Field(max_length=255)


class StreakRead(SQLModel):
    """Schema for reading user streak information."""

    current_streak: int
    longest_streak: int
    last_study_date: date | None = None
    days_studied_this_month: int
    streak_status: str  # "active" or "broken"
    message: str
