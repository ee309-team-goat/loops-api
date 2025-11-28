from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin


class UserBase(SQLModel):
    """Base User model with shared fields."""

    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    is_active: bool = Field(default=True, index=True)


class User(UserBase, TimestampMixin, table=True):
    """User database model."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    hashed_password: str = Field(max_length=255)

    # Streak tracking
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_study_date: Optional[date] = Field(default=None, index=True)
