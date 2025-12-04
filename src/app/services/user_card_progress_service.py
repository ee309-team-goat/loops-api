from datetime import datetime, timezone

from fsrs import Scheduler, Card, Rating, State as FSRSState
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import CardState, Deck, User, UserCardProgress, UserCardProgressCreate, UserSelectedDeck, VocabularyCard


class UserCardProgressService:
    """Service for user card progress CRUD operations and FSRS integration."""

    scheduler = Scheduler(enable_fuzzing=False)

    @staticmethod
    def progress_to_card(progress: UserCardProgress) -> Card:
        """Convert UserCardProgress to FSRS Card."""
        state_map = {
            CardState.NEW: FSRSState.Learning,  # New cards start as Learning in FSRS
            CardState.LEARNING: FSRSState.Learning,
            CardState.REVIEW: FSRSState.Review,
            CardState.RELEARNING: FSRSState.Relearning,
        }

        card = Card()
        card.state = state_map.get(progress.card_state, FSRSState.Learning)
        card.due = progress.next_review_date or datetime.now(timezone.utc)
        card.last_review = progress.last_review_date

        # Only set stability/difficulty if card has been reviewed before
        if progress.stability is not None and progress.stability > 0:
            card.stability = progress.stability
        if progress.difficulty is not None and progress.difficulty > 0:
            card.difficulty = progress.difficulty

        # Set step for learning/relearning states
        if card.state in (FSRSState.Learning, FSRSState.Relearning):
            card.step = 0

        return card

    @staticmethod
    def update_progress_from_card(
        progress: UserCardProgress,
        card: Card,
        is_correct: bool,
        review_datetime: datetime,
    ) -> UserCardProgress:
        """Update UserCardProgress from FSRS Card after review."""
        now = review_datetime

        # Calculate interval from due date
        interval_days = (card.due - now).days if card.due else 0

        # Track lapses (forgot card that was in Review state)
        was_review = progress.card_state == CardState.REVIEW
        if not is_correct and was_review:
            progress.lapses += 1

        # Update FSRS-computed values
        progress.stability = card.stability
        progress.difficulty = card.difficulty
        progress.next_review_date = card.due
        progress.last_review_date = now
        progress.interval = max(interval_days, 0)

        # Calculate elapsed days since last review
        if progress.last_review_date and progress.quality_history:
            last_review = progress.last_review_date
            progress.elapsed_days = (now - last_review).days
        else:
            progress.elapsed_days = 0

        # Map FSRS state back to our CardState
        state_map = {
            FSRSState.Learning: CardState.LEARNING,
            FSRSState.Review: CardState.REVIEW,
            FSRSState.Relearning: CardState.RELEARNING,
        }
        progress.card_state = state_map.get(card.state, CardState.LEARNING)

        # Update counters
        progress.total_reviews += 1
        progress.repetitions += 1
        if is_correct:
            progress.correct_count += 1

        # Record history
        history_entry = {
            "date": now.isoformat(),
            "is_correct": is_correct,
            "interval": interval_days,
            "stability": card.stability,
            "difficulty": card.difficulty,
            "state": progress.card_state.value,
        }

        if progress.quality_history is None:
            progress.quality_history = []
        if isinstance(progress.quality_history, list):
            progress.quality_history.append(history_entry)
        else:
            progress.quality_history = [history_entry]

        return progress

    @staticmethod
    async def create_progress(
        session: AsyncSession, progress_data: UserCardProgressCreate
    ) -> UserCardProgress:
        """Create a new user card progress."""
        progress = UserCardProgress(**progress_data.model_dump())
        session.add(progress)
        await session.commit()
        await session.refresh(progress)
        return progress

    @staticmethod
    async def get_progress(
        session: AsyncSession, progress_id: int
    ) -> UserCardProgress | None:
        """Get a user card progress by ID."""
        return await session.get(UserCardProgress, progress_id)

    @staticmethod
    async def get_user_card_progress(
        session: AsyncSession, user_id: int, card_id: int
    ) -> UserCardProgress | None:
        """Get progress for a specific user and card."""
        statement = select(UserCardProgress).where(
            UserCardProgress.user_id == user_id, UserCardProgress.card_id == card_id
        )
        result = await session.exec(statement)
        return result.one_or_none()

    @staticmethod
    async def get_user_progress(
        session: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[UserCardProgress]:
        """Get all progress entries for a user."""
        statement = (
            select(UserCardProgress)
            .where(UserCardProgress.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    @staticmethod
    async def get_due_cards(
        session: AsyncSession, user_id: int, limit: int = 20
    ) -> list[UserCardProgress]:
        """Get cards that are due for review."""
        now = datetime.now(timezone.utc)
        statement = (
            select(UserCardProgress)
            .where(
                UserCardProgress.user_id == user_id,
                UserCardProgress.next_review_date <= now,
            )
            .order_by(UserCardProgress.next_review_date)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    @staticmethod
    async def process_review(
        session: AsyncSession, user_id: int, card_id: int, is_correct: bool
    ) -> UserCardProgress:
        """
        Process a card review using FSRS algorithm.

        Binary rating:
        - Correct → Good (3)
        - Wrong → Again (1)
        """
        fsrs_rating = Rating.Good if is_correct else Rating.Again
        now = datetime.now(timezone.utc)

        progress = await UserCardProgressService.get_user_card_progress(
            session, user_id, card_id
        )

        if not progress:
            progress = UserCardProgress(
                user_id=user_id,
                card_id=card_id,
                card_state=CardState.NEW,
                next_review_date=now,
            )
            session.add(progress)

        # Convert to FSRS Card and process review
        card = UserCardProgressService.progress_to_card(progress)
        updated_card, _review_log = UserCardProgressService.scheduler.review_card(
            card=card,
            rating=fsrs_rating,
            review_datetime=now,
        )

        # Update progress from the reviewed card
        progress = UserCardProgressService.update_progress_from_card(
            progress, updated_card, is_correct, now
        )

        session.add(progress)
        await session.commit()
        await session.refresh(progress)

        return progress

    @staticmethod
    async def get_new_cards_count(
        session: AsyncSession, user_id: int
    ) -> dict:
        """
        Get count of new cards (not yet seen) and review cards (due for review).

        Respects user's deck selection settings:
        - If select_all_decks=true: count from all public decks
        - If select_all_decks=false: count from user_selected_decks only

        Returns:
            dict with new_cards_count and review_cards_count
        """
        # Get user to check deck selection preference
        user = await session.get(User, user_id)
        if not user:
            return {"new_cards_count": 0, "review_cards_count": 0}

        # Get cards user has already seen
        seen_subquery = select(UserCardProgress.card_id).where(
            UserCardProgress.user_id == user_id
        )

        # Build base query for new cards
        new_cards_query = select(func.count(VocabularyCard.id)).where(
            VocabularyCard.id.not_in(seen_subquery)
        )

        # Apply deck filtering based on user preference
        if user.select_all_decks:
            # Count from all public decks
            new_cards_query = new_cards_query.join(
                Deck, VocabularyCard.deck_id == Deck.id, isouter=True
            ).where(
                (Deck.is_public == True) | (VocabularyCard.deck_id == None)
            )
        else:
            # Count from selected decks only
            selected_deck_ids_subquery = select(UserSelectedDeck.deck_id).where(
                UserSelectedDeck.user_id == user_id
            )
            new_cards_query = new_cards_query.where(
                VocabularyCard.deck_id.in_(selected_deck_ids_subquery)
            )

        # Count new cards
        result = await session.exec(new_cards_query)
        new_cards_count = result.one()

        # Count review cards (due for review)
        now = datetime.now(timezone.utc)
        review_cards_query = select(func.count(UserCardProgress.id)).where(
            UserCardProgress.user_id == user_id,
            UserCardProgress.next_review_date <= now,
        )
        result = await session.exec(review_cards_query)
        review_cards_count = result.one()

        return {
            "new_cards_count": new_cards_count,
            "review_cards_count": review_cards_count,
        }
