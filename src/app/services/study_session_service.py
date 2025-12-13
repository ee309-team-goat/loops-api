"""
Study session service for managing study sessions and card selection.

Quiz 기능이 통합되어 세션 시작, 카드 요청, 정답 제출, 세션 완료를 모두 처리합니다.
"""

import math
import random
from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models import (
    AnswerResponse,
    AvailableCards,
    CardAllocation,
    CardResponse,
    CardState,
    ClozeQuestion,
    DailyGoalStatus,
    Deck,
    DueCardSummary,
    Profile,
    QuizType,
    SessionCompleteResponse,
    SessionPreviewResponse,
    SessionStartResponse,
    SessionStatus,
    SessionSummary,
    StreakInfo,
    StudyCard,
    StudyOverviewResponse,
    StudySession,
    UserCardProgress,
    UserSelectedDeck,
    VocabularyCard,
    XPInfo,
)
from app.services.profile_service import ProfileService
from app.services.user_card_progress_service import UserCardProgressService
from app.services.wrong_answer_service import WrongAnswerService

# CEFR level order for i+1 calculation
CEFR_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]


class StudySessionService:
    """Service for study session operations."""

    # ============================================================
    # Session Start
    # ============================================================

    @staticmethod
    async def start_session(
        session: AsyncSession,
        user_id: UUID,
        new_cards_limit: int | None = None,
        review_cards_limit: int | None = None,
        use_profile_ratio: bool = True,
    ) -> SessionStartResponse:
        """
        Start a new study session.

        Creates a StudySession record in DB and returns session info.
        Cards are NOT returned here - use get_next_card() to get each card.

        Args:
            session: DB session
            user_id: User ID
            new_cards_limit: Max new cards (ignored if use_profile_ratio=True)
            review_cards_limit: Max review cards (ignored if use_profile_ratio=True)
            use_profile_ratio: If True, calculate limits from profile settings
        """
        started_at = datetime.now(UTC)

        # Get profile for ratio calculation
        profile = await session.get(Profile, user_id)

        if use_profile_ratio and profile:
            # Calculate limits based on profile settings
            new_cards_limit, review_cards_limit = StudySessionService._calculate_card_limits(
                profile
            )
        else:
            # Use provided limits or defaults
            new_cards_limit = new_cards_limit if new_cards_limit is not None else 10
            review_cards_limit = review_cards_limit if review_cards_limit is not None else 20

        # Get new cards
        new_cards = await StudySessionService._get_new_cards(
            session, user_id, limit=new_cards_limit
        )

        # Get due review cards
        review_cards_data = await StudySessionService._get_due_review_cards(
            session, user_id, limit=review_cards_limit
        )

        # Build card ID list (new cards + review cards)
        card_ids = [card.id for card in new_cards]
        card_ids.extend([card.id for _, card in review_cards_data])

        # Shuffle for variety
        random.shuffle(card_ids)

        # Create StudySession record
        study_session = StudySession(
            user_id=user_id,
            new_cards_limit=new_cards_limit,
            review_cards_limit=review_cards_limit,
            status=SessionStatus.ACTIVE,
            card_ids=card_ids,
            current_index=0,
            correct_count=0,
            wrong_count=0,
            started_at=started_at,
        )

        session.add(study_session)
        await session.commit()
        await session.refresh(study_session)

        return SessionStartResponse(
            session_id=study_session.id,
            total_cards=len(card_ids),
            new_cards_count=len(new_cards),
            review_cards_count=len(review_cards_data),
            started_at=started_at,
        )

    @staticmethod
    async def start_session_with_cards(
        session: AsyncSession,
        user_id: UUID,
        card_ids: list[int],
    ) -> SessionStartResponse:
        """
        Start a new study session with specific card IDs.

        Used for wrong answer review sessions.

        Args:
            session: DB session
            user_id: User ID
            card_ids: List of card IDs to include in session
        """
        started_at = datetime.now(UTC)

        # Shuffle for variety
        random.shuffle(card_ids)

        # Create StudySession record
        study_session = StudySession(
            user_id=user_id,
            new_cards_limit=0,
            review_cards_limit=len(card_ids),
            status=SessionStatus.ACTIVE,
            card_ids=card_ids,
            current_index=0,
            correct_count=0,
            wrong_count=0,
            started_at=started_at,
        )

        session.add(study_session)
        await session.commit()
        await session.refresh(study_session)

        return SessionStartResponse(
            session_id=study_session.id,
            total_cards=len(card_ids),
            new_cards_count=0,
            review_cards_count=len(card_ids),
            started_at=started_at,
        )

    # ============================================================
    # Get Next Card
    # ============================================================

    @staticmethod
    async def get_next_card(
        session: AsyncSession,
        user_id: UUID,
        session_id: UUID,
        quiz_type: QuizType,
    ) -> CardResponse:
        """
        Get the next card in the session with quiz formatting.

        Args:
            session: DB session
            user_id: User ID (for validation)
            session_id: Study session ID
            quiz_type: Quiz type for this card

        Returns:
            CardResponse with formatted StudyCard or None if session complete
        """
        # Get study session
        study_session = await session.get(StudySession, session_id)
        if not study_session:
            raise NotFoundError(f"Session {session_id} not found")

        if study_session.user_id != user_id:
            raise ValidationError("Session does not belong to this user")

        if study_session.status != SessionStatus.ACTIVE:
            raise ValidationError(f"Session is {study_session.status.value}, not active")

        # Check if all cards completed
        total_cards = len(study_session.card_ids)
        if study_session.current_index >= total_cards:
            return CardResponse(
                card=None,
                cards_remaining=0,
                cards_completed=total_cards,
            )

        # Get current card
        card_id = study_session.card_ids[study_session.current_index]
        card = await session.get(VocabularyCard, card_id)
        if not card:
            raise NotFoundError(f"Card {card_id} not found")

        # Check if this card is new or review
        progress = await session.exec(
            select(UserCardProgress).where(
                UserCardProgress.user_id == user_id,
                UserCardProgress.card_id == card_id,
            )
        )
        existing_progress = progress.first()
        is_new = existing_progress is None

        # Format card based on quiz type
        study_card = await StudySessionService._format_card(session, card, quiz_type, is_new)

        # Increment current_index
        study_session.current_index += 1
        session.add(study_session)
        await session.commit()

        cards_remaining = total_cards - study_session.current_index

        return CardResponse(
            card=study_card,
            cards_remaining=cards_remaining,
            cards_completed=study_session.current_index - 1,  # Don't count current card
        )

    # ============================================================
    # Submit Answer
    # ============================================================

    @staticmethod
    async def submit_answer(
        session: AsyncSession,
        user_id: UUID,
        session_id: UUID,
        card_id: int,
        user_answer: str,
        response_time_ms: int | None = None,
        hint_count: int = 0,
        revealed_answer: bool = False,
        quiz_type: str | None = None,
    ) -> AnswerResponse:
        """
        Submit an answer and update FSRS progress.

        Args:
            session: DB session
            user_id: User ID
            session_id: Study session ID
            card_id: Card ID being answered
            user_answer: User's answer
            response_time_ms: Response time in milliseconds (optional)
            hint_count: Number of hints used (0 = no hints)
            revealed_answer: Whether the answer was revealed (show answer button)
            quiz_type: Quiz type used for this answer (for wrong answer tracking)

        Returns:
            AnswerResponse with correctness, score, and FSRS update info
        """
        # Get study session
        study_session = await session.get(StudySession, session_id)
        if not study_session:
            raise NotFoundError(f"Session {session_id} not found")

        if study_session.user_id != user_id:
            raise ValidationError("Session does not belong to this user")

        if study_session.status != SessionStatus.ACTIVE:
            raise ValidationError(f"Session is {study_session.status.value}, not active")

        # Verify card is in session
        if card_id not in study_session.card_ids:
            raise ValidationError("Card is not in this session")

        # Get card to determine correct answer
        card = await session.get(VocabularyCard, card_id)
        if not card:
            raise NotFoundError(f"Card {card_id} not found")

        # Determine correct answer based on typical quiz patterns
        # For word_to_meaning: korean_meaning is correct
        # For meaning_to_word, cloze, listening: english_word is correct
        # Since we don't know which quiz_type was used, we check both
        is_correct = (
            user_answer.strip().lower() == card.korean_meaning.strip().lower()
            or user_answer.strip().lower() == card.english_word.strip().lower()
        )

        # Calculate score based on hint usage (Issue #52)
        score, hint_penalty = StudySessionService._calculate_score(
            is_correct=is_correct,
            hint_count=hint_count,
            revealed_answer=revealed_answer,
        )

        # Determine FSRS rating based on hint usage
        # - revealed_answer: treat as incorrect (Again)
        # - hint_count > 0: treat as Hard (2)
        # - correct without hints: Good (3, default)
        fsrs_is_correct = is_correct and not revealed_answer
        fsrs_rating_hint = 2 if hint_count > 0 and is_correct else None  # 2 = Hard

        # Update FSRS progress
        progress = await UserCardProgressService.process_review(
            session=session,
            user_id=user_id,
            card_id=card_id,
            is_correct=fsrs_is_correct,
            rating_hint=fsrs_rating_hint,
        )

        # Update session counts (revealed_answer counts as wrong)
        if is_correct and not revealed_answer:
            study_session.correct_count += 1
        else:
            study_session.wrong_count += 1

            # Record wrong answer (Issue #53)
            await WrongAnswerService.create_wrong_answer(
                session=session,
                user_id=user_id,
                card_id=card_id,
                session_id=session_id,
                user_answer=user_answer,
                correct_answer=card.english_word,
                quiz_type=quiz_type or "unknown",
            )

        session.add(study_session)
        await session.commit()

        # Generate feedback
        if revealed_answer:
            feedback = f"정답: {card.korean_meaning} / {card.english_word}"
        elif is_correct:
            if hint_count > 0:
                feedback = f"정답입니다! (힌트 {hint_count}회 사용)"
            else:
                feedback = "정답입니다! 🎉"
        else:
            feedback = f"틀렸습니다. 정답: {card.korean_meaning} / {card.english_word}"

        return AnswerResponse(
            card_id=card_id,
            is_correct=is_correct,
            correct_answer=card.english_word,  # Primary answer
            user_answer=user_answer,
            feedback=feedback,
            score=score,
            hint_penalty=hint_penalty,
            next_review_date=progress.next_review_date,
            card_state=progress.card_state,
        )

    @staticmethod
    def _calculate_score(
        is_correct: bool,
        hint_count: int,
        revealed_answer: bool,
    ) -> tuple[int, int]:
        """
        Calculate score based on correctness and hint usage.

        Args:
            is_correct: Whether the answer was correct
            hint_count: Number of hints used
            revealed_answer: Whether the answer was revealed

        Returns:
            Tuple of (score, hint_penalty)
        """
        if revealed_answer:
            return 0, 0  # No score when answer revealed

        if not is_correct:
            return 0, 0  # No score for incorrect answer

        # Base score for correct answer
        base_score = 100
        penalty_per_hint = 20

        hint_penalty = min(hint_count * penalty_per_hint, base_score)
        score = max(0, base_score - hint_penalty)

        return score, hint_penalty

    # ============================================================
    # Session Complete
    # ============================================================

    @staticmethod
    async def complete_session(
        session: AsyncSession,
        user_id: UUID,
        session_id: UUID,
        duration_seconds: int | None = None,
    ) -> SessionCompleteResponse:
        """
        Complete a study session and update user statistics.

        Updates:
        - Session status to completed
        - User streak (consecutive study days)
        - Total study time
        - Returns session summary, streak info, XP, and daily goal status
        """
        # Get study session
        study_session = await session.get(StudySession, session_id)
        if not study_session:
            raise NotFoundError(f"Session {session_id} not found")

        if study_session.user_id != user_id:
            raise ValidationError("Session does not belong to this user")

        if study_session.status == SessionStatus.COMPLETED:
            raise ValidationError("Session already completed")

        # Get profile
        profile = await session.get(Profile, user_id)
        if not profile:
            raise NotFoundError(f"Profile {user_id} not found")

        # Calculate duration (use provided or calculate from timestamps)
        now = datetime.now(UTC)
        if duration_seconds is None:
            duration_seconds = int((now - study_session.started_at).total_seconds())

        # Update session status
        study_session.status = SessionStatus.COMPLETED
        study_session.completed_at = now
        session.add(study_session)

        # Calculate session summary
        total_cards = study_session.correct_count + study_session.wrong_count
        accuracy = (study_session.correct_count / total_cards * 100) if total_cards > 0 else 0.0

        session_summary = SessionSummary(
            total_cards=total_cards,
            correct=study_session.correct_count,
            wrong=study_session.wrong_count,
            accuracy=round(accuracy, 1),
            duration_seconds=duration_seconds,
        )

        # Calculate XP
        base_xp = study_session.correct_count * 10
        bonus_xp = 50 if accuracy >= 80.0 else 0
        total_xp = base_xp + bonus_xp

        xp_info = XPInfo(
            base_xp=base_xp,
            bonus_xp=bonus_xp,
            total_xp=total_xp,
        )

        # Update profile streak
        streak_result = await ProfileService.update_profile_streak(session, profile.id)
        message = StudySessionService._generate_streak_message(streak_result)

        streak_info = StreakInfo(
            current_streak=streak_result["current_streak"],
            longest_streak=streak_result["longest_streak"],
            is_new_record=streak_result["is_new_record"],
            streak_status=streak_result["streak_status"],
            message=message,
        )

        # Update total study time
        duration_minutes = duration_seconds // 60
        profile.total_study_time_minutes += duration_minutes
        session.add(profile)

        # Get daily goal status
        daily_goal_data = await ProfileService.get_daily_goal(session, profile.id)
        goal = daily_goal_data["daily_goal"]
        completed = daily_goal_data["completed_today"]
        progress = (completed / goal * 100) if goal > 0 else 0.0

        daily_goal_status = DailyGoalStatus(
            goal=goal,
            completed=completed,
            progress=round(min(progress, 100.0), 1),
            is_completed=completed >= goal,
        )

        await session.commit()

        return SessionCompleteResponse(
            session_summary=session_summary,
            streak=streak_info,
            daily_goal=daily_goal_status,
            xp=xp_info,
        )

    # ============================================================
    # Helper Methods: Card Selection
    # ============================================================

    @staticmethod
    def _get_next_cefr_level(current_cefr: str) -> str:
        """Get the next CEFR level (i+1). C2 stays at C2."""
        try:
            idx = CEFR_ORDER.index(current_cefr)
            if idx < len(CEFR_ORDER) - 1:
                return CEFR_ORDER[idx + 1]
            return current_cefr  # C2 stays at C2
        except ValueError:
            return "A1"  # Default fallback

    @staticmethod
    async def _get_new_cards(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 10,
    ) -> list[VocabularyCard]:
        """
        Get new cards user hasn't seen with i+1 CEFR logic.

        Cards are selected with 50/50 mix of current level (i) and next level (i+1).
        Fallback: if not enough cards, fill from other levels.
        """
        profile = await session.get(Profile, user_id)
        if not profile:
            return []

        # Get user's current CEFR level
        level_info = await ProfileService.calculate_profile_level(session, user_id)
        current_cefr = level_info["cefr_equivalent"]
        next_cefr = StudySessionService._get_next_cefr_level(current_cefr)

        # Calculate 50/50 split
        i_limit = math.ceil(limit / 2)
        i_plus_1_limit = math.floor(limit / 2)

        # Subquery for cards user has already seen
        seen_cards_subquery = select(UserCardProgress.card_id).where(
            UserCardProgress.user_id == user_id
        )

        # Helper to build base query with deck filtering
        def build_base_query():
            query = select(VocabularyCard).where(VocabularyCard.id.not_in(seen_cards_subquery))
            if profile.select_all_decks:
                query = query.outerjoin(Deck, VocabularyCard.deck_id == Deck.id).where(
                    (Deck.is_public == True) | (VocabularyCard.deck_id == None)  # noqa: E712, E711
                )
            else:
                selected_deck_ids_subquery = select(UserSelectedDeck.deck_id).where(
                    UserSelectedDeck.user_id == user_id
                )
                query = query.where(VocabularyCard.deck_id.in_(selected_deck_ids_subquery))
            return query

        # Get cards from current level (i)
        i_query = build_base_query().where(VocabularyCard.cefr_level == current_cefr)
        i_query = i_query.order_by(VocabularyCard.frequency_rank.asc().nullslast()).limit(i_limit)
        result = await session.exec(i_query)
        i_cards = list(result.all())

        # Get cards from next level (i+1)
        i_plus_1_cards = []
        if current_cefr != next_cefr:  # Only if not already at C2
            i_plus_1_query = build_base_query().where(VocabularyCard.cefr_level == next_cefr)
            i_plus_1_query = i_plus_1_query.order_by(
                VocabularyCard.frequency_rank.asc().nullslast()
            ).limit(i_plus_1_limit)
            result = await session.exec(i_plus_1_query)
            i_plus_1_cards = list(result.all())

        # Combine cards
        cards = i_cards + i_plus_1_cards

        # Fallback: if not enough cards, fill from current level first
        if len(cards) < limit:
            remaining = limit - len(cards)
            existing_ids = [c.id for c in cards]

            # Try to get more from current level
            fallback_i_query = (
                build_base_query()
                .where(VocabularyCard.cefr_level == current_cefr)
                .where(VocabularyCard.id.not_in(existing_ids))
            )
            fallback_i_query = fallback_i_query.order_by(
                VocabularyCard.frequency_rank.asc().nullslast()
            ).limit(remaining)
            result = await session.exec(fallback_i_query)
            fallback_i_cards = list(result.all())
            cards.extend(fallback_i_cards)
            existing_ids.extend([c.id for c in fallback_i_cards])

        # Fallback: if still not enough, get any unseen cards
        if len(cards) < limit:
            remaining = limit - len(cards)
            existing_ids = [c.id for c in cards]

            fallback_query = build_base_query().where(VocabularyCard.id.not_in(existing_ids))
            fallback_query = fallback_query.order_by(
                VocabularyCard.frequency_rank.asc().nullslast()
            ).limit(remaining)
            result = await session.exec(fallback_query)
            fallback_cards = list(result.all())
            cards.extend(fallback_cards)

        return cards

    @staticmethod
    async def _get_due_review_cards(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 20,
    ) -> list[tuple[UserCardProgress, VocabularyCard]]:
        """
        Get cards due for review (next_review_date <= now).

        Respects profile.review_scope setting:
        - selected_decks_only: Only review cards from selected decks
        - all_learned: Review all learned cards regardless of deck
        """
        now = datetime.now(UTC)

        # Get profile for review_scope setting
        profile = await session.get(Profile, user_id)

        query = (
            select(UserCardProgress, VocabularyCard)
            .join(VocabularyCard, VocabularyCard.id == UserCardProgress.card_id)
            .where(
                UserCardProgress.user_id == user_id,
                UserCardProgress.next_review_date <= now,
            )
        )

        # Apply deck filtering based on review_scope setting
        if profile and profile.review_scope == "selected_decks_only":
            # 선택된 덱의 카드만 복습
            if not profile.select_all_decks:
                selected_deck_ids_subquery = select(UserSelectedDeck.deck_id).where(
                    UserSelectedDeck.user_id == user_id
                )
                query = query.where(VocabularyCard.deck_id.in_(selected_deck_ids_subquery))
            # select_all_decks=True면 필터 없음 (모든 덱)
        # review_scope == "all_learned": 덱 필터 없이 모든 학습한 카드 복습

        query = query.order_by(UserCardProgress.next_review_date.asc()).limit(limit)

        result = await session.exec(query)
        return list(result.all())

    # ============================================================
    # Helper Methods: Card Formatting
    # ============================================================

    @staticmethod
    async def _format_card(
        session: AsyncSession,
        card: VocabularyCard,
        quiz_type: QuizType,
        is_new: bool,
    ) -> StudyCard:
        """Format a VocabularyCard as a StudyCard with quiz formatting."""
        question: str | ClozeQuestion
        options: list[str] | None = None

        if quiz_type == QuizType.WORD_TO_MEANING:
            question = card.english_word
            correct_answer = card.korean_meaning
            options = await StudySessionService._generate_options(
                session, correct_answer, quiz_type, card
            )

        elif quiz_type == QuizType.MEANING_TO_WORD:
            question = card.korean_meaning
            if card.part_of_speech:
                question = f"{question} ({card.part_of_speech})"
            correct_answer = card.english_word
            options = await StudySessionService._generate_options(
                session, correct_answer, quiz_type, card
            )

        elif quiz_type == QuizType.CLOZE:
            cloze = StudySessionService._generate_cloze_question(card)
            if cloze:
                question = cloze
                correct_answer = cloze.answer
                # Cloze is direct input, no options
                options = None
            else:
                # Fallback to word_to_meaning if no cloze available
                question = card.english_word
                correct_answer = card.korean_meaning
                options = await StudySessionService._generate_options(
                    session, correct_answer, QuizType.WORD_TO_MEANING, card
                )

        elif quiz_type == QuizType.LISTENING:
            question = "🔊 Listen and choose the correct word"
            correct_answer = card.english_word
            options = await StudySessionService._generate_options(
                session, correct_answer, quiz_type, card
            )

        else:
            # Default
            question = card.english_word
            correct_answer = card.korean_meaning

        return StudyCard(
            id=card.id,
            english_word=card.english_word,
            korean_meaning=card.korean_meaning,
            part_of_speech=card.part_of_speech,
            pronunciation_ipa=card.pronunciation_ipa,
            definition_en=card.definition_en,
            example_sentences=card.example_sentences,
            audio_url=card.audio_url,
            is_new=is_new,
            quiz_type=quiz_type,
            question=question,
            options=options,
        )

    @staticmethod
    async def _generate_options(
        session: AsyncSession,
        correct_answer: str,
        quiz_type: QuizType,
        card: VocabularyCard,
        count: int = 4,
    ) -> list[str]:
        """Generate multiple choice options."""
        wrong_answers: list[str] = []
        needed = count - 1

        # Get candidates with same difficulty/part of speech
        query = select(VocabularyCard).where(VocabularyCard.id != card.id)

        if card.difficulty_level:
            query = query.where(VocabularyCard.difficulty_level == card.difficulty_level)

        if card.part_of_speech:
            query = query.where(VocabularyCard.part_of_speech == card.part_of_speech)

        query = query.order_by(func.random()).limit(needed * 2)

        result = await session.exec(query)
        candidates = list(result.all())

        # Extract wrong answers based on quiz type
        for candidate in candidates:
            if len(wrong_answers) >= needed:
                break

            if quiz_type == QuizType.WORD_TO_MEANING:
                answer = candidate.korean_meaning
            else:
                answer = candidate.english_word

            if answer and answer.lower() != correct_answer.lower():
                if answer not in wrong_answers:
                    wrong_answers.append(answer)

        # Fallback if not enough candidates
        if len(wrong_answers) < needed:
            fallback_query = (
                select(VocabularyCard)
                .where(VocabularyCard.id != card.id)
                .order_by(func.random())
                .limit(needed * 2)
            )
            result = await session.exec(fallback_query)
            fallback_candidates = list(result.all())

            for candidate in fallback_candidates:
                if len(wrong_answers) >= needed:
                    break

                if quiz_type == QuizType.WORD_TO_MEANING:
                    answer = candidate.korean_meaning
                else:
                    answer = candidate.english_word

                if answer and answer.lower() != correct_answer.lower():
                    if answer not in wrong_answers:
                        wrong_answers.append(answer)

        # Shuffle options
        options = [correct_answer] + wrong_answers[:needed]
        random.shuffle(options)

        return options

    # ============================================================
    # Helper Methods: Cloze Generation
    # ============================================================

    @staticmethod
    def _generate_cloze_question(card: VocabularyCard) -> ClozeQuestion | None:
        """
        Generate a cloze question from a card.

        Uses cloze_sentences if available, otherwise generates from example_sentences.
        """
        import re

        word = card.english_word.lower()

        # Try pre-generated cloze_sentences first
        if card.cloze_sentences and len(card.cloze_sentences) > 0:
            cloze_data = card.cloze_sentences[0]
            if isinstance(cloze_data, dict):
                return ClozeQuestion(
                    sentence_with_blank=cloze_data.get("sentence_with_blank", ""),
                    hint=cloze_data.get("hint", ""),
                    answer=cloze_data.get("answer", card.english_word),
                    blank_position=cloze_data.get("blank_position", 0),
                )

        # Generate from example_sentences
        if card.example_sentences and len(card.example_sentences) > 0:
            example = card.example_sentences[0]
            sentence = example.get("en", "") if isinstance(example, dict) else str(example)

            if sentence:
                # Replace word with blank (case insensitive)
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                sentence_with_blank = pattern.sub("______", sentence)

                if sentence_with_blank != sentence:
                    # Generate hint
                    hint = f"{word[0]}로 시작하는 {len(word)}글자"
                    if card.part_of_speech:
                        hint += f" ({card.part_of_speech})"

                    return ClozeQuestion(
                        sentence_with_blank=sentence_with_blank,
                        hint=hint,
                        answer=card.english_word,
                        blank_position=sentence.lower().find(word),
                    )

        return None

    # ============================================================
    # Helper Methods: Card Limits Calculation
    # ============================================================

    @staticmethod
    def _calculate_card_limits(profile: Profile) -> tuple[int, int]:
        """
        Calculate new_cards_limit and review_cards_limit based on profile settings.

        Args:
            profile: User profile with review ratio settings

        Returns:
            Tuple of (new_cards_limit, review_cards_limit)

        Modes:
        - normal: 새 단어 최소 min_new_ratio(25%) 보장
        - custom: 복습 비율 custom_review_ratio 그대로 적용

        Examples:
        - normal mode, daily_goal=20, min_new_ratio=0.25:
          -> new=5 (25%), review=15 (75%)
        - custom mode, daily_goal=20, custom_review_ratio=0.6:
          -> new=8 (40%), review=12 (60%)
        """
        daily_goal = profile.daily_goal

        if profile.review_ratio_mode == "custom":
            # Custom mode: use custom_review_ratio directly
            review_ratio = profile.custom_review_ratio
            new_ratio = 1.0 - review_ratio
        else:
            # Normal mode: guarantee minimum new ratio
            new_ratio = profile.min_new_ratio
            review_ratio = 1.0 - new_ratio

        new_cards_limit = max(1, int(daily_goal * new_ratio))
        review_cards_limit = max(1, int(daily_goal * review_ratio))

        # Ensure limits don't exceed maximums
        new_cards_limit = min(new_cards_limit, 50)
        review_cards_limit = min(review_cards_limit, 100)

        return new_cards_limit, review_cards_limit

    # ============================================================
    # Helper Methods: Messages
    # ============================================================

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

    # ============================================================
    # Study Overview
    # ============================================================

    @staticmethod
    async def get_overview(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 50,
    ) -> StudyOverviewResponse:
        """
        Get study overview with card counts and due cards list.

        Args:
            session: DB session
            user_id: User ID
            limit: Maximum number of due cards to return

        Returns:
            StudyOverviewResponse with counts, due cards, and daily goal progress
        """
        # Get counts using existing service method
        count_data = await UserCardProgressService.get_new_cards_count(session, user_id)
        new_cards_count = count_data["new_cards_count"]
        review_cards_count = count_data["review_cards_count"]

        # Get due cards with details
        due_progress_list = await UserCardProgressService.get_due_cards(
            session, user_id, limit=limit
        )

        # Build due cards summary list
        due_cards: list[DueCardSummary] = []
        for progress in due_progress_list:
            # Get card details
            card = await session.get(VocabularyCard, progress.card_id)
            if card:
                due_cards.append(
                    DueCardSummary(
                        card_id=progress.card_id,
                        english_word=card.english_word,
                        korean_meaning=card.korean_meaning,
                        next_review_date=progress.next_review_date,
                        card_state=progress.card_state,
                    )
                )

        # Get profile for daily_goal
        profile = await session.get(Profile, user_id)
        if not profile:
            raise NotFoundError(f"Profile not found for user {user_id}", resource="profile")

        daily_goal_value = profile.daily_goal or 30

        # Calculate today's completed cards from StudySession
        now = datetime.now(UTC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Query today's completed sessions
        sessions_query = select(StudySession).where(
            StudySession.user_id == user_id,
            StudySession.started_at >= today_start,
            StudySession.started_at <= today_end,
            StudySession.completed_at.isnot(None),
        )
        result = await session.exec(sessions_query)
        sessions = result.all()

        # Sum cards from all completed sessions today
        total_cards_today = sum(s.correct_count + s.wrong_count for s in sessions)

        # Calculate progress
        progress_value = (
            min((total_cards_today / daily_goal_value) * 100, 100.0)
            if daily_goal_value > 0
            else 0.0
        )
        is_completed = total_cards_today >= daily_goal_value

        daily_goal_status = DailyGoalStatus(
            goal=daily_goal_value,
            completed=total_cards_today,
            progress=round(progress_value, 1),
            is_completed=is_completed,
        )

        return StudyOverviewResponse(
            new_cards_count=new_cards_count,
            review_cards_count=review_cards_count,
            total_available=new_cards_count + review_cards_count,
            due_cards=due_cards,
            daily_goal=daily_goal_status,
        )

    @staticmethod
    async def preview_session(
        session: AsyncSession,
        user_id: UUID,
        total_cards: int,
        review_ratio: float,
    ) -> SessionPreviewResponse:
        """
        Preview session allocation based on total cards and review ratio.

        Args:
            session: DB session
            user_id: User ID
            total_cards: Total cards to study
            review_ratio: Ratio of review cards (0.0-1.0)

        Returns:
            SessionPreviewResponse with available and allocated cards
        """
        # Get counts using existing service method
        count_data = await UserCardProgressService.get_new_cards_count(session, user_id)
        new_cards_available = count_data["new_cards_count"]
        review_cards_available = count_data["review_cards_count"]

        # Get relearning cards count (RELEARNING state)
        relearning_query = select(func.count(UserCardProgress.id)).where(
            UserCardProgress.user_id == user_id,
            UserCardProgress.card_state == CardState.RELEARNING,
        )
        result = await session.exec(relearning_query)
        relearning_cards_available = result.one() or 0

        # Calculate allocation based on ratio
        review_cards_requested = int(total_cards * review_ratio)
        new_cards_requested = total_cards - review_cards_requested

        # Adjust allocation based on availability
        review_cards_allocated = min(review_cards_requested, review_cards_available)
        new_cards_allocated = min(new_cards_requested, new_cards_available)

        # Adjust if we can't meet the requested total
        actual_total = review_cards_allocated + new_cards_allocated

        # Try to fill remaining slots from the other type if available
        if actual_total < total_cards:
            shortage = total_cards - actual_total
            if (
                new_cards_allocated < new_cards_requested
                and new_cards_available > new_cards_allocated
            ):
                # Try to add more new cards
                additional_new = min(shortage, new_cards_available - new_cards_allocated)
                new_cards_allocated += additional_new
                actual_total += additional_new
                shortage -= additional_new

            if (
                shortage > 0
                and review_cards_allocated < review_cards_requested
                and review_cards_available > review_cards_allocated
            ):
                # Try to add more review cards
                additional_review = min(shortage, review_cards_available - review_cards_allocated)
                review_cards_allocated += additional_review
                actual_total += additional_review

        # Generate warning message if we can't meet the request
        message = None
        if actual_total < total_cards:
            missing = total_cards - actual_total
            message = f"요청한 {total_cards}개의 카드 중 {missing}개가 부족합니다. {actual_total}개의 카드만 사용할 수 있습니다."
        elif (
            review_cards_allocated < review_cards_requested
            or new_cards_allocated < new_cards_requested
        ):
            message = f"요청한 비율대로 배정할 수 없어 조정되었습니다. 신규 {new_cards_allocated}개, 복습 {review_cards_allocated}개가 배정됩니다."

        available = AvailableCards(
            new_cards=new_cards_available,
            review_cards=review_cards_available,
            relearning_cards=relearning_cards_available,
        )

        allocation = CardAllocation(
            new_cards=new_cards_allocated,
            review_cards=review_cards_allocated,
            total=actual_total,
        )

        return SessionPreviewResponse(
            available=available,
            allocation=allocation,
            message=message,
        )
