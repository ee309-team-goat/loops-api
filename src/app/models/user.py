import enum
from datetime import date, datetime
from typing import Optional

from sqlmodel import Column, Enum, Field, SQLModel

from app.models.base import TimestampMixin


class SubscriptionType(str, enum.Enum):
    """Subscription type enum."""

    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class UserBase(SQLModel):
    """Base User model with shared fields."""

    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=255)
    occupation: Optional[str] = Field(default=None, max_length=100)
    language_level: Optional[str] = Field(default=None, max_length=50)  # beginner, intermediate, advanced
    learning_goal: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True, index=True)
    is_verified: bool = Field(default=False)
    is_premium: bool = Field(default=False)


class User(UserBase, TimestampMixin, table=True):
    """User database model."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    hashed_password: str = Field(max_length=255)

    # Subscription
    subscription_type: SubscriptionType = Field(
        default=SubscriptionType.FREE, sa_column=Column(Enum(SubscriptionType), nullable=False)
    )

    # Streak tracking
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_study_date: Optional[date] = Field(default=None, index=True)

    # Learning statistics
    total_cards_learned: int = Field(default=0)
    total_study_time_minutes: int = Field(default=0)

    # Session tracking
    last_login_at: Optional[datetime] = Field(default=None)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(min_length=8, max_length=255)


class UserRead(UserBase):
    """Schema for reading a user."""

    id: int
    subscription_type: SubscriptionType
    current_streak: int
    longest_streak: int
    last_study_date: Optional[date] = None
    total_cards_learned: int
    total_study_time_minutes: int
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(SQLModel):
    """Schema for updating a user."""

    email: Optional[str] = Field(default=None, max_length=255)
    username: Optional[str] = Field(default=None, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=255)
    occupation: Optional[str] = Field(default=None, max_length=100)
    language_level: Optional[str] = Field(default=None, max_length=50)
    learning_goal: Optional[str] = None
    subscription_type: Optional[SubscriptionType] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_premium: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)


class UserLogin(SQLModel):
    """Schema for user login."""

    username: str = Field(max_length=100)
    password: str = Field(max_length=255)
