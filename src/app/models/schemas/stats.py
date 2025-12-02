from sqlmodel import SQLModel


class TotalLearnedRead(SQLModel):
    """Schema for reading total learned statistics."""

    total_learned: int
    by_level: dict[str, int]
    total_study_time_minutes: int
