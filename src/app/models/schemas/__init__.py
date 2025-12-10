from app.models.schemas.deck import (
    DeckCreate,
    DeckDetailRead,
    DeckRead,
    DecksListResponse,
    DeckUpdate,
    DeckWithProgressRead,
)
from app.models.schemas.favorite import FavoriteCreate, FavoriteRead
from app.models.schemas.profile import (
    DailyGoalRead,
    ProfileConfigRead,
    ProfileConfigUpdate,
    ProfileLevelRead,
    ProfileRead,
    ProfileUpdate,
    StreakRead,
)
from app.models.schemas.stats import (
    AccuracyByPeriod,
    StatsAccuracyRead,
    StatsHistoryItem,
    StatsHistoryRead,
    StatsHistorySummary,
    TodayStatsRead,
    TodayVocabularyStats,
    TotalLearnedRead,
)
from app.models.schemas.study import (
    AnswerRequest,
    AnswerResponse,
    CardRequest,
    CardResponse,
    ClozeQuestion,
    DailyGoalStatus,
    DueCardSummary,
    SessionCompleteRequest,
    SessionCompleteResponse,
    SessionStartRequest,
    SessionStartResponse,
    SessionSummary,
    StreakInfo,
    StudyCard,
    StudyOverviewResponse,
    XPInfo,
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
    # Profile
    "ProfileRead",
    "ProfileUpdate",
    "DailyGoalRead",
    "StreakRead",
    "ProfileConfigRead",
    "ProfileConfigUpdate",
    "ProfileLevelRead",
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
    "StatsHistorySummary",
    "StatsAccuracyRead",
    "AccuracyByPeriod",
    "TodayStatsRead",
    "TodayVocabularyStats",
    # Study Session
    "SessionStartRequest",
    "SessionStartResponse",
    "CardRequest",
    "CardResponse",
    "StudyCard",
    "ClozeQuestion",
    "AnswerRequest",
    "AnswerResponse",
    "SessionCompleteRequest",
    "SessionCompleteResponse",
    "SessionSummary",
    "StreakInfo",
    "DailyGoalStatus",
    "XPInfo",
    # Study Overview
    "DueCardSummary",
    "StudyOverviewResponse",
]
