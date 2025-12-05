from datetime import date

from sqlmodel import SQLModel


class TotalLearnedRead(SQLModel):
    """Schema for reading total learned statistics."""

    total_learned: int
    by_level: dict[str, int]
    total_study_time_minutes: int


class StatsHistoryItem(SQLModel):
    """Schema for a single day's study history."""

    date: date
    cards_studied: int
    correct_count: int
    accuracy_rate: float


class StatsHistoryRead(SQLModel):
    """Schema for reading study history (for charts)."""

    period: str  # "7d", "30d", "90d", "1y"
    data: list[StatsHistoryItem]


class AccuracyByPeriod(SQLModel):
    """Schema for accuracy statistics by time period."""

    all_time: float
    last_7_days: float | None = None
    last_30_days: float | None = None
    last_90_days: float | None = None


class StatsAccuracyRead(SQLModel):
    """Schema for reading accuracy statistics."""

    overall_accuracy: float
    total_reviews: int
    total_correct: int
    by_period: AccuracyByPeriod
    by_cefr_level: dict[str, float]  # e.g., {"A1": 85.0, "A2": 78.5}
    trend: str  # "improving", "stable", "declining"
