from datetime import date, datetime
from typing import Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.user import UserBase


class UserCreate(UserBase):
    """Schema for creating a user."""

    email: EmailStr = Field(max_length=255)  # Email validation
    password: str = Field(min_length=8, max_length=255)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username is alphanumeric and not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty or whitespace")
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v

    @field_validator("daily_goal")
    @classmethod
    def daily_goal_positive(cls, v: int) -> int:
        """Validate daily goal is positive."""
        if v <= 0:
            raise ValueError("Daily goal must be greater than 0")
        if v > 1000:
            raise ValueError("Daily goal cannot exceed 1000")
        return v

    @field_validator("theme")
    @classmethod
    def theme_valid(cls, v: str) -> str:
        """Validate theme is one of the allowed values."""
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v


class UserRead(UserBase):
    """Schema for reading a user."""

    id: int
    current_streak: int
    longest_streak: int
    last_study_date: Optional[date] = None
    select_all_decks: bool
    daily_goal: int
    timezone: str
    theme: str
    notification_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(SQLModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = Field(default=None, max_length=255)
    username: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)
    select_all_decks: Optional[bool] = None
    daily_goal: Optional[int] = Field(default=None, gt=0, le=1000)
    timezone: Optional[str] = Field(default=None, max_length=50)
    theme: Optional[str] = Field(default=None, max_length=20)
    notification_enabled: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: Optional[str]) -> Optional[str]:
        """Validate username is alphanumeric and not just whitespace."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Username cannot be empty or whitespace")
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength."""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v

    @field_validator("theme")
    @classmethod
    def theme_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validate theme is one of the allowed values."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v


class UserLogin(SQLModel):
    """Schema for user login."""

    username: str = Field(max_length=100)
    password: str = Field(max_length=255)


class DailyGoalRead(SQLModel):
    """Schema for reading daily goal information."""

    daily_goal: int
    completed_today: int
