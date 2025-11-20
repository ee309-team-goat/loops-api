from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class StudySessionBase(SQLModel):
    """Base StudySession model with shared fields."""

    user_id: int = Field(foreign_key="users.id", index=True)
    deck_id: Optional[int] = Field(default=None, foreign_key="decks.id", index=True)
    session_date: date = Field(index=True)
    duration_minutes: int = Field(default=0)
    cards_studied: int = Field(default=0)
    correct_answers: int = Field(default=0)
    wrong_answers: int = Field(default=0)
    accuracy_rate: float = Field(default=0.0)


class StudySession(StudySessionBase, table=True):
    """StudySession database model for tracking study sessions."""

    __tablename__ = "study_sessions"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    started_at: datetime
    ended_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StudySessionCreate(StudySessionBase):
    """Schema for creating a study session."""

    started_at: datetime


class StudySessionRead(StudySessionBase):
    """Schema for reading a study session."""

    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime


class StudySessionUpdate(SQLModel):
    """Schema for updating a study session."""

    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    cards_studied: Optional[int] = None
    correct_answers: Optional[int] = None
    wrong_answers: Optional[int] = None
    accuracy_rate: Optional[float] = None
