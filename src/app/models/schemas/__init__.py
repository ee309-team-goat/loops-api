from app.models.schemas.deck import (
    DeckCreate,
    DeckDetailRead,
    DeckRead,
    DecksListResponse,
    DeckUpdate,
    DeckWithProgressRead,
)
from app.models.schemas.favorite import FavoriteCreate, FavoriteRead
from app.models.schemas.stats import (
    AccuracyByPeriod,
    StatsAccuracyRead,
    StatsHistoryItem,
    StatsHistoryRead,
    TotalLearnedRead,
)
from app.models.schemas.study import (
    DailyGoalStatus,
    SessionCard,
    SessionCompleteRequest,
    SessionCompleteResponse,
    SessionStartRequest,
    SessionStartResponse,
    SessionSummary,
    StreakInfo,
)
from app.models.schemas.user import (
    DailyGoalRead,
    StreakRead,
    UserConfigRead,
    UserConfigUpdate,
    UserCreate,
    UserLevelRead,
    UserLogin,
    UserRead,
    UserUpdate,
)
from app.models.schemas.user_card_progress import (
    NewCardsCountRead,
    ReviewRequest,
    TodayProgressRead,
    UserCardProgressCreate,
    UserCardProgressRead,
)
from app.models.schemas.user_selected_deck import (
    GetSelectedDecksResponse,
    SelectDecksRequest,
    SelectDecksResponse,
    SelectedDeckInfo,
    UserSelectedDeckCreate,
    UserSelectedDeckRead,
)
from app.models.schemas.vocabulary_card import (
    VocabularyCardCreate,
    VocabularyCardRead,
    VocabularyCardUpdate,
)

__all__ = [
    # User
    "UserRead",
    "UserUpdate",
    "UserCreate",
    "UserLogin",
    "DailyGoalRead",
    "StreakRead",
    "UserConfigRead",
    "UserConfigUpdate",
    "UserLevelRead",
    # VocabularyCard
    "VocabularyCardCreate",
    "VocabularyCardRead",
    "VocabularyCardUpdate",
    # UserCardProgress
    "UserCardProgressCreate",
    "UserCardProgressRead",
    "ReviewRequest",
    "TodayProgressRead",
    "NewCardsCountRead",
    # Deck
    "DeckCreate",
    "DeckRead",
    "DeckUpdate",
    "DeckWithProgressRead",
    "DeckDetailRead",
    "DecksListResponse",
    # Favorite
    "FavoriteCreate",
    "FavoriteRead",
    # UserSelectedDeck
    "UserSelectedDeckCreate",
    "UserSelectedDeckRead",
    "SelectDecksRequest",
    "SelectDecksResponse",
    "SelectedDeckInfo",
    "GetSelectedDecksResponse",
    # Stats
    "TotalLearnedRead",
    "StatsHistoryRead",
    "StatsHistoryItem",
    "StatsAccuracyRead",
    "AccuracyByPeriod",
    # Study Session
    "SessionCompleteRequest",
    "SessionCompleteResponse",
    "SessionStartRequest",
    "SessionStartResponse",
    "SessionCard",
    "SessionSummary",
    "StreakInfo",
    "DailyGoalStatus",
]
