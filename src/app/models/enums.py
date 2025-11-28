import enum


class CardState(str, enum.Enum):
    """Card state enum for FSRS algorithm."""

    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"

