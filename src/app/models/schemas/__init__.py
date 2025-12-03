from app.models.schemas.deck import DeckCreate, DeckRead, DeckUpdate
from app.models.schemas.favorite import FavoriteCreate, FavoriteRead
from app.models.schemas.user import DailyGoalRead, UserCreate, UserLogin, UserRead, UserUpdate
from app.models.schemas.user_card_progress import (
    ReviewRequest,
    UserCardProgressCreate,
    UserCardProgressRead,
)
from app.models.schemas.user_selected_deck import (
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
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "UserLogin",
    "DailyGoalRead",
    # VocabularyCard
    "VocabularyCardCreate",
    "VocabularyCardRead",
    "VocabularyCardUpdate",
    # UserCardProgress
    "UserCardProgressCreate",
    "UserCardProgressRead",
    "ReviewRequest",
    # Deck
    "DeckCreate",
    "DeckRead",
    "DeckUpdate",
    # Favorite
    "FavoriteCreate",
    "FavoriteRead",
    # UserSelectedDeck
    "UserSelectedDeckCreate",
    "UserSelectedDeckRead",
]
