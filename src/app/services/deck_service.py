"""
Deck service for calculating deck progress statistics.
"""

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Deck,
    DecksListResponse,
    DeckWithProgressRead,
    UserCardProgress,
    VocabularyCard,
)
from app.models.enums import CardState


class DeckService:
    """Service for deck-related operations."""

    @staticmethod
    async def get_decks_list(
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> DecksListResponse:
        """
        Get list of all accessible decks with progress information.

        Returns public decks and user's own decks with learning progress statistics.
        """
        # Query for accessible decks (public or created by user)
        decks_query = (
            select(Deck)
            .where((Deck.is_public == True) | (Deck.creator_id == user_id))
            .offset(skip)
            .limit(limit)
        )
        result = await session.exec(decks_query)
        decks = list(result.all())

        # Count total accessible decks
        count_query = select(func.count(Deck.id)).where(
            (Deck.is_public == True) | (Deck.creator_id == user_id)
        )
        result = await session.exec(count_query)
        total_count = result.one()

        # Calculate progress for each deck
        decks_with_progress = []
        for deck in decks:
            progress = await DeckService.calculate_deck_progress(session, user_id, deck.id)
            deck_dict = {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                **progress,
            }
            decks_with_progress.append(DeckWithProgressRead(**deck_dict))

        return DecksListResponse(
            decks=decks_with_progress,
            total=total_count,
            skip=skip,
            limit=limit,
        )

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
        learned_query = (
            select(func.count(UserCardProgress.id))
            .select_from(VocabularyCard)
            .join(
                UserCardProgress,
                (VocabularyCard.id == UserCardProgress.card_id)
                & (UserCardProgress.user_id == user_id),
            )
            .where(
                VocabularyCard.deck_id == deck_id,
                UserCardProgress.card_state == CardState.REVIEW,
            )
        )
        result = await session.exec(learned_query)
        learned_cards = result.one()

        # Count LEARNING + RELEARNING cards
        learning_query = (
            select(func.count(UserCardProgress.id))
            .select_from(VocabularyCard)
            .join(
                UserCardProgress,
                (VocabularyCard.id == UserCardProgress.card_id)
                & (UserCardProgress.user_id == user_id),
            )
            .where(
                VocabularyCard.deck_id == deck_id,
                UserCardProgress.card_state.in_([CardState.LEARNING, CardState.RELEARNING]),
            )
        )
        result = await session.exec(learning_query)
        learning_cards = result.one()

        # Count cards with progress (any state)
        cards_with_progress_query = (
            select(func.count(UserCardProgress.id))
            .select_from(VocabularyCard)
            .join(
                UserCardProgress,
                (VocabularyCard.id == UserCardProgress.card_id)
                & (UserCardProgress.user_id == user_id),
            )
            .where(VocabularyCard.deck_id == deck_id)
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
