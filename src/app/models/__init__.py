# Base
from app.models.base import TimestampMixin

# Enums
from app.models.enums import CardState

# Schemas (DTOs)
from app.models.schemas import (
    AccuracyByPeriod,
    DailyGoalRead,
    DailyGoalStatus,
    DeckCreate,
    DeckDetailRead,
    DeckRead,
    DecksListResponse,
    DeckUpdate,
    DeckWithProgressRead,
    FavoriteCreate,
    FavoriteRead,
    GetSelectedDecksResponse,
    NewCardsCountRead,
    ReviewRequest,
    SelectDecksRequest,
    SelectDecksResponse,
    SelectedDeckInfo,
    SessionCard,
    SessionCompleteRequest,
    SessionCompleteResponse,
    SessionStartRequest,
    SessionStartResponse,
    SessionSummary,
    StatsAccuracyRead,
    StatsHistoryItem,
    StatsHistoryRead,
    StreakInfo,
    StreakRead,
    TodayProgressRead,
    UserCardProgressCreate,
    UserCardProgressRead,
    UserConfigRead,
    UserConfigUpdate,
    UserCreate,
    UserLevelRead,
    UserLogin,
    UserRead,
    UserSelectedDeckCreate,
    UserSelectedDeckRead,
    UserUpdate,
    VocabularyCardCreate,
    VocabularyCardRead,
    VocabularyCardUpdate,
)

# Tables (DB Models) - includes Base classes
from app.models.tables import (
    Deck,
    DeckBase,
    Favorite,
    User,
    UserBase,
    UserCardProgress,
    UserCardProgressBase,
    UserSelectedDeck,
    VocabularyCard,
    VocabularyCardBase,
)

__all__ = [
    # Base
    "TimestampMixin",
    # Enums
    "CardState",
    # Tables
    "User",
    "VocabularyCard",
    "UserCardProgress",
    "Deck",
    "Favorite",
    "UserSelectedDeck",
    # Base classes (from tables)
    "UserBase",
    "VocabularyCardBase",
    "UserCardProgressBase",
    "DeckBase",
    # User Schemas
    "UserRead",
    "UserUpdate",
    "UserCreate",
    "UserLogin",
    "DailyGoalRead",
    "StreakRead",
    "UserConfigRead",
    "UserConfigUpdate",
    "UserLevelRead",
    # VocabularyCard Schemas
    "VocabularyCardCreate",
    "VocabularyCardRead",
    "VocabularyCardUpdate",
    # UserCardProgress Schemas
    "UserCardProgressCreate",
    "UserCardProgressRead",
    "ReviewRequest",
    "TodayProgressRead",
    "NewCardsCountRead",
    # Deck Schemas
    "DeckCreate",
    "DeckRead",
    "DeckUpdate",
    "DeckWithProgressRead",
    "DeckDetailRead",
    "DecksListResponse",
    # Favorite Schemas
    "FavoriteCreate",
    "FavoriteRead",
    # UserSelectedDeck Schemas
    "UserSelectedDeckCreate",
    "UserSelectedDeckRead",
    "SelectDecksRequest",
    "SelectDecksResponse",
    "SelectedDeckInfo",
    "GetSelectedDecksResponse",
    # Stats Schemas
    "StatsHistoryRead",
    "StatsHistoryItem",
    "StatsAccuracyRead",
    "AccuracyByPeriod",
    # Study Session Schemas
    "SessionCompleteRequest",
    "SessionCompleteResponse",
    "SessionStartRequest",
    "SessionStartResponse",
    "SessionCard",
    "SessionSummary",
    "StreakInfo",
    "DailyGoalStatus",
]
