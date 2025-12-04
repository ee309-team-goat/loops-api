from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import VocabularyCard, VocabularyCardCreate, VocabularyCardUpdate


class VocabularyCardService:
    """Service for vocabulary card CRUD operations."""

    @staticmethod
    async def create_card(session: AsyncSession, card_data: VocabularyCardCreate) -> VocabularyCard:
        """Create a new vocabulary card."""
        card = VocabularyCard(**card_data.model_dump())
        session.add(card)
        await session.commit()
        await session.refresh(card)
        return card

    @staticmethod
    async def get_card(session: AsyncSession, card_id: int) -> VocabularyCard | None:
        """Get a vocabulary card by ID."""
        return await session.get(VocabularyCard, card_id)

    @staticmethod
    async def get_cards(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        difficulty_level: str | None = None,
        deck_id: int | None = None,
    ) -> list[VocabularyCard]:
        """Get a list of vocabulary cards with optional filtering."""
        statement = select(VocabularyCard)

        if difficulty_level:
            statement = statement.where(VocabularyCard.difficulty_level == difficulty_level)
        if deck_id is not None:
            statement = statement.where(VocabularyCard.deck_id == deck_id)

        statement = statement.offset(skip).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    @staticmethod
    async def update_card(
        session: AsyncSession, card_id: int, card_data: VocabularyCardUpdate
    ) -> VocabularyCard | None:
        """Update a vocabulary card."""
        card = await VocabularyCardService.get_card(session, card_id)
        if not card:
            return None

        update_dict = card_data.model_dump(exclude_unset=True)
        card.sqlmodel_update(update_dict)

        session.add(card)
        await session.commit()
        await session.refresh(card)
        return card

    @staticmethod
    async def delete_card(session: AsyncSession, card_id: int) -> bool:
        """Delete a vocabulary card."""
        card = await VocabularyCardService.get_card(session, card_id)
        if not card:
            return False

        await session.delete(card)
        await session.commit()
        return True
