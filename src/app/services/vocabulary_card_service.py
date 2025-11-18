from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.vocabulary_card import VocabularyCard, VocabularyCardCreate, VocabularyCardUpdate


class VocabularyCardService:
    """Service for vocabulary card CRUD operations."""

    @staticmethod
    async def create_card(
        session: AsyncSession, card_data: VocabularyCardCreate
    ) -> VocabularyCard:
        """
        Create a new vocabulary card.

        Args:
            session: Database session
            card_data: Card creation data

        Returns:
            Created vocabulary card
        """
        card = VocabularyCard(**card_data.model_dump())
        session.add(card)
        await session.commit()
        await session.refresh(card)
        return card

    @staticmethod
    async def get_card(session: AsyncSession, card_id: int) -> VocabularyCard | None:
        """
        Get a vocabulary card by ID.

        Args:
            session: Database session
            card_id: Card ID

        Returns:
            Vocabulary card if found, None otherwise
        """
        statement = select(VocabularyCard).where(VocabularyCard.id == card_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_cards(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        difficulty_level: Optional[str] = None,
        deck_id: Optional[int] = None,
    ) -> list[VocabularyCard]:
        """
        Get a list of vocabulary cards with optional filtering.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            difficulty_level: Filter by difficulty level
            deck_id: Filter by deck ID

        Returns:
            List of vocabulary cards
        """
        statement = select(VocabularyCard)

        # Apply filters
        if difficulty_level:
            statement = statement.where(VocabularyCard.difficulty_level == difficulty_level)
        if deck_id is not None:
            statement = statement.where(VocabularyCard.deck_id == deck_id)

        statement = statement.offset(skip).limit(limit)
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def get_cards_by_deck(
        session: AsyncSession, deck_id: int, skip: int = 0, limit: int = 100
    ) -> list[VocabularyCard]:
        """
        Get all vocabulary cards in a specific deck.

        Args:
            session: Database session
            deck_id: Deck ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of vocabulary cards in the deck
        """
        statement = (
            select(VocabularyCard)
            .where(VocabularyCard.deck_id == deck_id)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def search_cards(
        session: AsyncSession, search_term: str, skip: int = 0, limit: int = 100
    ) -> list[VocabularyCard]:
        """
        Search vocabulary cards by word or translation.

        Args:
            session: Database session
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching vocabulary cards
        """
        statement = (
            select(VocabularyCard)
            .where(
                (VocabularyCard.word.ilike(f"%{search_term}%"))
                | (VocabularyCard.translation.ilike(f"%{search_term}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def update_card(
        session: AsyncSession, card_id: int, card_data: VocabularyCardUpdate
    ) -> VocabularyCard | None:
        """
        Update a vocabulary card.

        Args:
            session: Database session
            card_id: Card ID
            card_data: Update data

        Returns:
            Updated vocabulary card if found, None otherwise
        """
        card = await VocabularyCardService.get_card(session, card_id)
        if not card:
            return None

        update_dict = card_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(card, key, value)

        session.add(card)
        await session.commit()
        await session.refresh(card)
        return card

    @staticmethod
    async def delete_card(session: AsyncSession, card_id: int) -> bool:
        """
        Delete a vocabulary card.

        Args:
            session: Database session
            card_id: Card ID

        Returns:
            True if deleted, False if not found
        """
        card = await VocabularyCardService.get_card(session, card_id)
        if not card:
            return False

        await session.delete(card)
        await session.commit()
        return True
