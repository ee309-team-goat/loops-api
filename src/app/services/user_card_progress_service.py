from datetime import datetime, timezone

from fsrs import FSRS, Card, Rating, State as FSRSState
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.user_card_progress import (
    CardState,
    UserCardProgress,
    UserCardProgressCreate,
    UserCardProgressUpdate,
)


class UserCardProgressService:
    """Service for user card progress CRUD operations and FSRS integration."""

    # Initialize FSRS scheduler
    fsrs = FSRS()

    @staticmethod
    def progress_to_card(progress: UserCardProgress) -> Card:
        """
        Convert UserCardProgress to FSRS Card.

        Args:
            progress: UserCardProgress model

        Returns:
            FSRS Card object
        """
        card = Card()

        # Map card state
        if progress.card_state == CardState.NEW:
            card.state = FSRSState.New
        elif progress.card_state == CardState.LEARNING:
            card.state = FSRSState.Learning
        elif progress.card_state == CardState.REVIEW:
            card.state = FSRSState.Review
        elif progress.card_state == CardState.RELEARNING:
            card.state = FSRSState.Relearning

        # Map FSRS parameters
        card.due = progress.next_review_date
        card.stability = progress.stability or 0.0
        card.difficulty = progress.difficulty or 0.0
        card.reps = progress.repetitions
        card.lapses = progress.lapses
        card.elapsed_days = progress.elapsed_days
        card.scheduled_days = progress.interval or 0
        card.last_review = progress.last_review_date

        return card

    @staticmethod
    def update_progress_from_card(
        progress: UserCardProgress, card: Card, rating: Rating
    ) -> UserCardProgress:
        """
        Update UserCardProgress from FSRS Card after review.

        Args:
            progress: UserCardProgress model to update
            card: FSRS Card with updated values
            rating: Rating given in review

        Returns:
            Updated UserCardProgress
        """
        # Update FSRS fields
        progress.stability = card.stability
        progress.difficulty = card.difficulty
        progress.repetitions = card.reps
        progress.lapses = card.lapses
        progress.next_review_date = card.due
        progress.last_review_date = datetime.now(timezone.utc)
        progress.interval = card.scheduled_days
        progress.elapsed_days = card.elapsed_days

        # Update state
        if card.state == FSRSState.New:
            progress.card_state = CardState.NEW
        elif card.state == FSRSState.Learning:
            progress.card_state = CardState.LEARNING
        elif card.state == FSRSState.Review:
            progress.card_state = CardState.REVIEW
        elif card.state == FSRSState.Relearning:
            progress.card_state = CardState.RELEARNING

        # Update statistics
        progress.total_reviews += 1
        if rating in [Rating.Good, Rating.Easy]:
            progress.correct_count += 1

        # Append to quality_history (JSONB)
        history_entry = {
            "date": progress.last_review_date.isoformat(),
            "quality": rating,
            "interval": card.scheduled_days,
            "stability": card.stability,
            "difficulty": card.difficulty,
        }

        if progress.quality_history is None:
            progress.quality_history = []
        if isinstance(progress.quality_history, list):
            progress.quality_history.append(history_entry)
        else:
            # Handle case where it might be stored as dict
            progress.quality_history = [history_entry]

        return progress

    @staticmethod
    async def create_progress(
        session: AsyncSession, progress_data: UserCardProgressCreate
    ) -> UserCardProgress:
        """
        Create a new user card progress.

        Args:
            session: Database session
            progress_data: Progress creation data

        Returns:
            Created user card progress
        """
        progress = UserCardProgress(**progress_data.model_dump())
        session.add(progress)
        await session.commit()
        await session.refresh(progress)
        return progress

    @staticmethod
    async def get_progress(
        session: AsyncSession, progress_id: int
    ) -> UserCardProgress | None:
        """
        Get a user card progress by ID.

        Args:
            session: Database session
            progress_id: Progress ID

        Returns:
            User card progress if found, None otherwise
        """
        statement = select(UserCardProgress).where(UserCardProgress.id == progress_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_card_progress(
        session: AsyncSession, user_id: int, card_id: int
    ) -> UserCardProgress | None:
        """
        Get progress for a specific user and card.

        Args:
            session: Database session
            user_id: User ID
            card_id: Card ID

        Returns:
            User card progress if found, None otherwise
        """
        statement = select(UserCardProgress).where(
            UserCardProgress.user_id == user_id, UserCardProgress.card_id == card_id
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_progress(
        session: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[UserCardProgress]:
        """
        Get all progress entries for a user.

        Args:
            session: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user card progress entries
        """
        statement = (
            select(UserCardProgress)
            .where(UserCardProgress.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def get_due_cards(
        session: AsyncSession, user_id: int, limit: int = 20
    ) -> list[UserCardProgress]:
        """
        Get cards that are due for review.

        Args:
            session: Database session
            user_id: User ID
            limit: Maximum number of cards to return

        Returns:
            List of user card progress entries due for review
        """
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
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def get_new_cards(
        session: AsyncSession, user_id: int, limit: int = 20
    ) -> list[UserCardProgress]:
        """
        Get new cards to learn.

        Args:
            session: Database session
            user_id: User ID
            limit: Maximum number of cards to return

        Returns:
            List of new user card progress entries
        """
        statement = (
            select(UserCardProgress)
            .where(
                UserCardProgress.user_id == user_id,
                UserCardProgress.card_state == CardState.NEW,
            )
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def process_review(
        session: AsyncSession, user_id: int, card_id: int, rating: int
    ) -> UserCardProgress:
        """
        Process a card review using FSRS algorithm.

        Args:
            session: Database session
            user_id: User ID
            card_id: Card ID
            rating: Rating (1=Again, 2=Hard, 3=Good, 4=Easy)

        Returns:
            Updated user card progress

        Raises:
            ValueError: If rating is invalid
        """
        # Validate rating
        if rating not in [1, 2, 3, 4]:
            raise ValueError(
                "Rating must be 1 (Again), 2 (Hard), 3 (Good), or 4 (Easy)"
            )

        # Map integer to Rating enum
        rating_map = {1: Rating.Again, 2: Rating.Hard, 3: Rating.Good, 4: Rating.Easy}
        fsrs_rating = rating_map[rating]

        # Get or create progress
        progress = await UserCardProgressService.get_user_card_progress(
            session, user_id, card_id
        )

        if not progress:
            # Create new progress for new card
            now = datetime.now(timezone.utc)
            progress = UserCardProgress(
                user_id=user_id,
                card_id=card_id,
                card_state=CardState.NEW,
                next_review_date=now,
            )
            session.add(progress)

        # Convert to FSRS Card
        card = UserCardProgressService.progress_to_card(progress)

        # Get scheduling for current review
        now = datetime.now(timezone.utc)
        scheduling_cards = UserCardProgressService.fsrs.repeat(card, now)

        # Apply the user's rating
        card_info = scheduling_cards[fsrs_rating]
        updated_card = card_info.card

        # Update progress from FSRS result
        progress = UserCardProgressService.update_progress_from_card(
            progress, updated_card, fsrs_rating
        )

        session.add(progress)
        await session.commit()
        await session.refresh(progress)

        return progress

    @staticmethod
    async def update_progress(
        session: AsyncSession, progress_id: int, progress_data: UserCardProgressUpdate
    ) -> UserCardProgress | None:
        """
        Update a user card progress.

        Args:
            session: Database session
            progress_id: Progress ID
            progress_data: Update data

        Returns:
            Updated user card progress if found, None otherwise
        """
        progress = await UserCardProgressService.get_progress(session, progress_id)
        if not progress:
            return None

        update_dict = progress_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(progress, key, value)

        session.add(progress)
        await session.commit()
        await session.refresh(progress)
        return progress

    @staticmethod
    async def get_progress_statistics(
        session: AsyncSession, user_id: int
    ) -> dict[str, any]:
        """
        Get user's progress statistics.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Dictionary with statistics
        """
        statement = select(UserCardProgress).where(UserCardProgress.user_id == user_id)
        result = await session.execute(statement)
        progress_entries = list(result.scalars().all())

        if not progress_entries:
            return {
                "total_cards": 0,
                "new_cards": 0,
                "learning_cards": 0,
                "review_cards": 0,
                "mastered_cards": 0,
                "average_accuracy": 0.0,
            }

        total_cards = len(progress_entries)
        new_cards = sum(1 for p in progress_entries if p.card_state == CardState.NEW)
        learning_cards = sum(
            1 for p in progress_entries if p.card_state == CardState.LEARNING
        )
        review_cards = sum(
            1 for p in progress_entries if p.card_state == CardState.REVIEW
        )
        mastered_cards = review_cards  # Cards in review state are considered mastered

        # Calculate average accuracy
        total_reviews = sum(p.total_reviews for p in progress_entries)
        correct_reviews = sum(p.correct_count for p in progress_entries)
        avg_accuracy = (
            (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0.0
        )

        return {
            "total_cards": total_cards,
            "new_cards": new_cards,
            "learning_cards": learning_cards,
            "review_cards": review_cards,
            "mastered_cards": mastered_cards,
            "average_accuracy": round(avg_accuracy, 2),
        }
