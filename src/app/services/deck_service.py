"""
Deck service for calculating deck progress statistics.
"""

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserCardProgress, VocabularyCard
from app.models.enums import CardState


class DeckService:
    """Service for deck-related operations."""

    @staticmethod
    async def calculate_deck_progress(
        session: AsyncSession,
        user_id: int,
        deck_id: int,
    ) -> dict:
        """
        Calculate deck learning progress for a user.

        Returns:
            {
                "total_cards": int,
                "learned_cards": int,  # REVIEW state
                "learning_cards": int,  # LEARNING/RELEARNING
                "new_cards": int,  # Not in UserCardProgress
                "progress_percent": float
            }
        """
        # Count total cards in deck
        total_cards_query = select(func.count(VocabularyCard.id)).where(
            VocabularyCard.deck_id == deck_id
        )
        result = await session.exec(total_cards_query)
        total_cards = result.one()

        # Handle empty deck
        if total_cards == 0:
            return {
                "total_cards": 0,
                "learned_cards": 0,
                "learning_cards": 0,
                "new_cards": 0,
                "progress_percent": 0.0,
            }

        # Count cards by state using JOIN
        # Count REVIEW (learned) cards
        learned_query = select(func.count(UserCardProgress.id)).select_from(
            VocabularyCard
        ).join(
            UserCardProgress,
            (VocabularyCard.id == UserCardProgress.card_id)
            & (UserCardProgress.user_id == user_id),
        ).where(
            VocabularyCard.deck_id == deck_id,
            UserCardProgress.card_state == CardState.REVIEW,
        )
        result = await session.exec(learned_query)
        learned_cards = result.one()

        # Count LEARNING + RELEARNING cards
        learning_query = select(func.count(UserCardProgress.id)).select_from(
            VocabularyCard
        ).join(
            UserCardProgress,
            (VocabularyCard.id == UserCardProgress.card_id)
            & (UserCardProgress.user_id == user_id),
        ).where(
            VocabularyCard.deck_id == deck_id,
            UserCardProgress.card_state.in_([CardState.LEARNING, CardState.RELEARNING]),
        )
        result = await session.exec(learning_query)
        learning_cards = result.one()

        # Count cards with progress (any state)
        cards_with_progress_query = select(func.count(UserCardProgress.id)).select_from(
            VocabularyCard
        ).join(
            UserCardProgress,
            (VocabularyCard.id == UserCardProgress.card_id)
            & (UserCardProgress.user_id == user_id),
        ).where(
            VocabularyCard.deck_id == deck_id
        )
        result = await session.exec(cards_with_progress_query)
        cards_with_progress = result.one()

        # Calculate new cards (cards without any progress)
        new_cards = total_cards - cards_with_progress

        # Calculate progress percentage (learned / total * 100)
        progress_percent = (learned_cards / total_cards * 100) if total_cards > 0 else 0.0

        return {
            "total_cards": total_cards,
            "learned_cards": learned_cards,
            "learning_cards": learning_cards,
            "new_cards": new_cards,
            "progress_percent": round(progress_percent, 1),
        }
