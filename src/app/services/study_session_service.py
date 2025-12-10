"""
Study session service for managing study sessions and card selection.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    DailyGoalStatus,
    Deck,
    Profile,
    SessionCard,
    SessionCompleteResponse,
    SessionStartResponse,
    SessionSummary,
    StreakInfo,
    UserCardProgress,
    UserSelectedDeck,
    VocabularyCard,
)
from app.services.profile_service import ProfileService


class StudySessionService:
    """Service for study session operations."""

    @staticmethod
    async def get_new_cards_for_session(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 10,
    ) -> list[VocabularyCard]:
        """
        Get new cards user hasn't seen, ordered by frequency rank.

        Respects user's deck selection:
        - If select_all_decks=true: get from all public decks
        - If select_all_decks=false: get from selected decks only

        Cards are ordered by frequency_rank ASC (most common words first).
        """
        # Get profile to check deck selection preference
        profile = await session.get(Profile, user_id)
        if not profile:
            return []

        # Subquery for cards user has already seen
        seen_cards_subquery = select(UserCardProgress.card_id).where(
            UserCardProgress.user_id == user_id
        )

        # Build query for unseen cards
        query = select(VocabularyCard).where(VocabularyCard.id.not_in(seen_cards_subquery))

        # Apply deck filtering based on user preference
        if profile.select_all_decks:
            # Get from all public decks (or cards without a deck)
            query = query.outerjoin(Deck, VocabularyCard.deck_id == Deck.id).where(
                (Deck.is_public == True) | (VocabularyCard.deck_id == None)  # noqa: E712, E711
            )
        else:
            # Get from selected decks only
            selected_deck_ids_subquery = select(UserSelectedDeck.deck_id).where(
                UserSelectedDeck.user_id == user_id
            )
            query = query.where(VocabularyCard.deck_id.in_(selected_deck_ids_subquery))

        # Order by frequency rank (most common words first)
        # Cards without frequency_rank go last
        query = query.order_by(VocabularyCard.frequency_rank.asc().nullslast()).limit(limit)

        result = await session.exec(query)
        return list(result.all())

    @staticmethod
    async def get_due_review_cards(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 20,
    ) -> list[tuple[UserCardProgress, VocabularyCard]]:
        """
        Get cards due for review (next_review_date <= now).

        Returns list of (progress, card) tuples.
        """
        now = datetime.now(UTC)

        query = (
            select(UserCardProgress, VocabularyCard)
            .join(VocabularyCard, VocabularyCard.id == UserCardProgress.card_id)
            .where(
                UserCardProgress.user_id == user_id,
                UserCardProgress.next_review_date <= now,
            )
            .order_by(UserCardProgress.next_review_date.asc())
            .limit(limit)
        )

        result = await session.exec(query)
        return list(result.all())

    @staticmethod
    async def start_session(
        session: AsyncSession,
        user_id: UUID,
        new_cards_limit: int = 10,
        review_cards_limit: int = 20,
    ) -> SessionStartResponse:
        """
        Start a new study session.

        Returns session data with mixed new and review cards.
        """
        session_id = str(uuid4())
        started_at = datetime.now(UTC)

        # Get new cards
        new_cards = await StudySessionService.get_new_cards_for_session(
            session, user_id, limit=new_cards_limit
        )

        # Get due review cards
        review_cards_data = await StudySessionService.get_due_review_cards(
            session, user_id, limit=review_cards_limit
        )

        # Build session cards list
        session_cards: list[SessionCard] = []

        # Add new cards (is_new=True)
        for card in new_cards:
            session_cards.append(
                SessionCard(
                    id=card.id,
                    english_word=card.english_word,
                    korean_meaning=card.korean_meaning,
                    part_of_speech=card.part_of_speech,
                    pronunciation_ipa=card.pronunciation_ipa,
                    definition_en=card.definition_en,
                    example_sentences=card.example_sentences,
                    is_new=True,
                )
            )

        # Add review cards (is_new=False)
        for _progress, card in review_cards_data:
            session_cards.append(
                SessionCard(
                    id=card.id,
                    english_word=card.english_word,
                    korean_meaning=card.korean_meaning,
                    part_of_speech=card.part_of_speech,
                    pronunciation_ipa=card.pronunciation_ipa,
                    definition_en=card.definition_en,
                    example_sentences=card.example_sentences,
                    is_new=False,
                )
            )

        return SessionStartResponse(
            session_id=session_id,
            total_cards=len(session_cards),
            new_cards_count=len(new_cards),
            review_cards_count=len(review_cards_data),
            cards=session_cards,
            started_at=started_at,
        )

    @staticmethod
    def _generate_streak_message(streak_result: dict) -> str:
        """Generate user-friendly streak message."""
        if streak_result["is_new_record"]:
            return f"🏆 최고 기록 달성! {streak_result['longest_streak']}일!"

        if streak_result["streak_status"] == "continued":
            return f"🔥 {streak_result['current_streak']}일 연속 학습 중!"
        elif streak_result["streak_status"] == "started":
            return "🎉 새로운 학습 여정을 시작했어요!"
        else:  # broken
            return "💪 다시 시작해요! 오늘이 새로운 시작입니다!"

    @staticmethod
    async def complete_session(
        session: AsyncSession,
        profile: Profile,
        cards_studied: int,
        cards_correct: int,
        duration_seconds: int,
    ) -> SessionCompleteResponse:
        """
        Complete a study session and update user statistics.

        Updates:
        - User streak (consecutive study days)
        - Total study time
        - Returns session summary, streak info, and daily goal status
        """
        # 1. Calculate session summary
        wrong_count = cards_studied - cards_correct
        accuracy = (cards_studied / cards_studied * 100) if cards_studied > 0 else 0.0

        session_summary = SessionSummary(
            total_cards=cards_studied,
            correct=cards_correct,
            wrong=wrong_count,
            accuracy=round(accuracy, 1),
            duration_seconds=duration_seconds,
        )

        # 2. Update profile streak
        streak_result = await ProfileService.update_profile_streak(session, profile.id)
        message = StudySessionService._generate_streak_message(streak_result)

        streak_info = StreakInfo(
            current_streak=streak_result["current_streak"],
            longest_streak=streak_result["longest_streak"],
            is_new_record=streak_result["is_new_record"],
            streak_status=streak_result["streak_status"],
            message=message,
        )

        # 3. Update total study time
        duration_minutes = duration_seconds // 60
        profile.total_study_time_minutes += duration_minutes
        session.add(profile)

        # 4. Get daily goal status
        daily_goal_data = await ProfileService.get_daily_goal(session, profile.id)
        goal = daily_goal_data["daily_goal"]
        completed = daily_goal_data["completed_today"]
        progress = (completed / goal * 100) if goal > 0 else 0.0

        daily_goal_status = DailyGoalStatus(
            goal=goal,
            completed=completed,
            progress=round(progress, 1),
            is_completed=completed >= goal,
        )

        # 5. Commit changes
        await session.commit()

        return SessionCompleteResponse(
            session_summary=session_summary,
            streak=streak_info,
            daily_goal=daily_goal_status,
        )
