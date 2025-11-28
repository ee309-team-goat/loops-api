from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.tables.user import UserBase


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(min_length=8, max_length=255)


class UserRead(UserBase):
    """Schema for reading a user."""

    id: int
    current_streak: int
    longest_streak: int
    last_study_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(SQLModel):
    """Schema for updating a user."""

    email: Optional[str] = Field(default=None, max_length=255)
    username: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)


class UserLogin(SQLModel):
    """Schema for user login."""

    username: str = Field(max_length=100)
    password: str = Field(max_length=255)
