# Base
from app.models.base import TimestampMixin

# Enums
from app.models.enums import CardState

# Schemas (DTOs)
from app.models.schemas import (
    DailyGoalRead,
    DeckCreate,
    DeckRead,
    DecksListResponse,
    DeckUpdate,
    DeckWithProgressRead,
    FavoriteCreate,
    FavoriteRead,
    GetSelectedDecksResponse,
    NewCardsCountRead,
    ReviewRequest,
    SelectedDeckInfo,
    SelectDecksRequest,
    SelectDecksResponse,
    TodayProgressRead,
    UserCardProgressCreate,
    UserCardProgressRead,
    UserCreate,
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
    "DailyGoalRead",
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
]
