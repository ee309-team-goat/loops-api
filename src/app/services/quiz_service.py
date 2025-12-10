"""
퀴즈 서비스.

4가지 퀴즈 모드(word_to_meaning, meaning_to_word, cloze, listening)를 지원하고
4지선다 오답 생성 로직을 포함합니다.
"""

import random
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    AnswerResult,
    Deck,
    Profile,
    QuizCard,
    QuizSessionResponse,
    QuizType,
    UserCardProgress,
    UserSelectedDeck,
    VocabularyCard,
)
from app.services.cloze_service import ClozeService


class QuizService:
    """퀴즈 서비스."""

    @staticmethod
    async def get_cards_for_quiz(
        session: AsyncSession,
        user_id: UUID,
        quiz_type: QuizType,
        limit: int = 10,
        include_new: bool = True,
        include_review: bool = True,
    ) -> list[VocabularyCard]:
        """
        퀴즈에 사용할 카드를 가져옵니다.

        Args:
            session: DB 세션
            user_id: 사용자 ID
            quiz_type: 퀴즈 유형
            limit: 최대 카드 수
            include_new: 새 카드 포함 여부
            include_review: 복습 카드 포함 여부

        Returns:
            VocabularyCard 목록
        """
        # Get profile for deck preferences
        profile = await session.get(Profile, user_id)
        if not profile:
            return []

        cards: list[VocabularyCard] = []
        now = datetime.now(UTC)

        # 1. 복습 카드 가져오기 (include_review가 True인 경우)
        if include_review:
            review_query = (
                select(VocabularyCard)
                .join(UserCardProgress, VocabularyCard.id == UserCardProgress.card_id)
                .where(
                    UserCardProgress.user_id == user_id,
                    UserCardProgress.next_review_date <= now,
                )
            )

            # 듣기 모드는 audio_url이 있는 카드만
            if quiz_type == QuizType.LISTENING:
                review_query = review_query.where(VocabularyCard.audio_url.isnot(None))

            # Cloze는 example_sentences가 있거나 cloze_sentences가 있는 카드
            if quiz_type == QuizType.CLOZE:
                review_query = review_query.where(
                    (VocabularyCard.example_sentences.isnot(None))
                    | (VocabularyCard.cloze_sentences.isnot(None))
                )

            review_query = review_query.order_by(UserCardProgress.next_review_date.asc())
            review_query = review_query.limit(limit)

            result = await session.exec(review_query)
            cards.extend(result.all())

        # 2. 새 카드 가져오기 (include_new가 True이고 아직 limit에 못 미친 경우)
        remaining = limit - len(cards)
        if include_new and remaining > 0:
            # 이미 본 카드 제외
            seen_cards_subquery = select(UserCardProgress.card_id).where(
                UserCardProgress.user_id == user_id
            )

            new_query = select(VocabularyCard).where(VocabularyCard.id.not_in(seen_cards_subquery))

            # 덱 필터링
            if profile.select_all_decks:
                new_query = new_query.outerjoin(Deck, VocabularyCard.deck_id == Deck.id).where(
                    (Deck.is_public == True) | (VocabularyCard.deck_id == None)  # noqa: E712, E711
                )
            else:
                selected_deck_ids = select(UserSelectedDeck.deck_id).where(
                    UserSelectedDeck.user_id == user_id
                )
                new_query = new_query.where(VocabularyCard.deck_id.in_(selected_deck_ids))

            # 퀴즈 타입별 필터
            if quiz_type == QuizType.LISTENING:
                new_query = new_query.where(VocabularyCard.audio_url.isnot(None))

            if quiz_type == QuizType.CLOZE:
                new_query = new_query.where(
                    (VocabularyCard.example_sentences.isnot(None))
                    | (VocabularyCard.cloze_sentences.isnot(None))
                )

            new_query = new_query.order_by(VocabularyCard.frequency_rank.asc().nullslast()).limit(
                remaining
            )

            result = await session.exec(new_query)
            cards.extend(result.all())

        # 순서 셔플
        random.shuffle(cards)

        return cards

    @staticmethod
    async def generate_options(
        session: AsyncSession,
        correct_answer: str,
        quiz_type: QuizType,
        card: VocabularyCard,
        count: int = 4,
    ) -> list[str]:
        """
        4지선다 오답을 생성합니다.

        Args:
            session: DB 세션
            correct_answer: 정답
            quiz_type: 퀴즈 유형
            card: 현재 카드 (난이도/품사 매칭용)
            count: 총 선택지 수 (정답 포함)

        Returns:
            셔플된 선택지 목록
        """
        wrong_answers: list[str] = []
        needed = count - 1  # 정답 제외

        # 같은 난이도/품사의 카드에서 오답 선택
        query = select(VocabularyCard).where(VocabularyCard.id != card.id)

        # 난이도가 있으면 같은 난이도에서 우선 선택
        if card.difficulty_level:
            query = query.where(VocabularyCard.difficulty_level == card.difficulty_level)

        # 품사가 있으면 같은 품사에서 우선 선택
        if card.part_of_speech:
            query = query.where(VocabularyCard.part_of_speech == card.part_of_speech)

        query = query.order_by(func.random()).limit(needed * 2)  # 여유 있게 가져옴

        result = await session.exec(query)
        candidates = list(result.all())

        # 퀴즈 타입에 따라 오답 추출
        for candidate in candidates:
            if len(wrong_answers) >= needed:
                break

            if quiz_type == QuizType.WORD_TO_MEANING:
                # 뜻 맞추기: korean_meaning이 오답
                answer = candidate.korean_meaning
            elif quiz_type == QuizType.MEANING_TO_WORD:
                # 단어 맞추기: english_word가 오답
                answer = candidate.english_word
            elif quiz_type == QuizType.CLOZE:
                # 빈칸 채우기: english_word가 오답
                answer = candidate.english_word
            else:  # LISTENING
                # 듣기: english_word가 오답
                answer = candidate.english_word

            # 중복 방지
            if answer and answer.lower() != correct_answer.lower():
                if answer not in wrong_answers:
                    wrong_answers.append(answer)

        # 난이도/품사 필터에서 충분하지 않으면 추가 쿼리
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

                if quiz_type in (QuizType.WORD_TO_MEANING,):
                    answer = candidate.korean_meaning
                else:
                    answer = candidate.english_word

                if answer and answer.lower() != correct_answer.lower():
                    if answer not in wrong_answers:
                        wrong_answers.append(answer)

        # 정답 포함하여 셔플
        options = [correct_answer] + wrong_answers[:needed]
        random.shuffle(options)

        return options

    @staticmethod
    async def format_as_word_to_meaning(
        session: AsyncSession,
        card: VocabularyCard,
    ) -> QuizCard:
        """영어 단어 → 뜻 맞추기 형식으로 포맷합니다."""
        options = await QuizService.generate_options(
            session=session,
            correct_answer=card.korean_meaning,
            quiz_type=QuizType.WORD_TO_MEANING,
            card=card,
        )

        return QuizCard(
            card_id=card.id,
            quiz_type=QuizType.WORD_TO_MEANING,
            question=card.english_word,
            answer=card.korean_meaning,
            options=options,
            audio_url=card.audio_url,
            extra_info={
                "part_of_speech": card.part_of_speech,
                "pronunciation_ipa": card.pronunciation_ipa,
                "definition_en": card.definition_en,
            },
        )

    @staticmethod
    async def format_as_meaning_to_word(
        session: AsyncSession,
        card: VocabularyCard,
    ) -> QuizCard:
        """뜻 → 영어 단어 맞추기 형식으로 포맷합니다."""
        options = await QuizService.generate_options(
            session=session,
            correct_answer=card.english_word,
            quiz_type=QuizType.MEANING_TO_WORD,
            card=card,
        )

        # 힌트로 뜻과 품사 제공
        question = card.korean_meaning
        if card.part_of_speech:
            question = f"{question} ({card.part_of_speech})"

        return QuizCard(
            card_id=card.id,
            quiz_type=QuizType.MEANING_TO_WORD,
            question=question,
            answer=card.english_word,
            options=options,
            audio_url=None,  # 뜻→단어는 오디오 제공하지 않음
            extra_info={
                "definition_en": card.definition_en,
                "pronunciation_ipa": card.pronunciation_ipa,
            },
        )

    @staticmethod
    async def format_as_cloze(
        session: AsyncSession,
        card: VocabularyCard,
    ) -> QuizCard | None:
        """빈칸 채우기 형식으로 포맷합니다."""
        cloze_questions = ClozeService.get_or_generate_cloze(card, max_count=1)

        if not cloze_questions:
            return None

        cloze = cloze_questions[0]

        # 빈칸에 들어갈 오답 생성
        options = await QuizService.generate_options(
            session=session,
            correct_answer=cloze.answer,
            quiz_type=QuizType.CLOZE,
            card=card,
        )

        return QuizCard(
            card_id=card.id,
            quiz_type=QuizType.CLOZE,
            question=cloze,  # ClozeQuestion 객체
            answer=cloze.answer,
            options=options,
            audio_url=cloze.audio_url,
            extra_info={
                "hint": cloze.hint,
                "korean_meaning": card.korean_meaning,
            },
        )

    @staticmethod
    async def format_as_listening(
        session: AsyncSession,
        card: VocabularyCard,
    ) -> QuizCard | None:
        """듣기 형식으로 포맷합니다."""
        if not card.audio_url:
            return None

        options = await QuizService.generate_options(
            session=session,
            correct_answer=card.english_word,
            quiz_type=QuizType.LISTENING,
            card=card,
        )

        return QuizCard(
            card_id=card.id,
            quiz_type=QuizType.LISTENING,
            question="🔊 Listen and choose the correct word",
            answer=card.english_word,
            options=options,
            audio_url=card.audio_url,
            extra_info={
                "korean_meaning": card.korean_meaning,
                "pronunciation_ipa": card.pronunciation_ipa,
            },
        )

    @staticmethod
    async def start_quiz_session(
        session: AsyncSession,
        user_id: UUID,
        quiz_type: QuizType,
        cards_limit: int = 10,
        include_new: bool = True,
        include_review: bool = True,
    ) -> QuizSessionResponse:
        """
        퀴즈 세션을 시작합니다.

        Args:
            session: DB 세션
            user_id: 사용자 ID
            quiz_type: 퀴즈 유형
            cards_limit: 최대 카드 수
            include_new: 새 카드 포함
            include_review: 복습 카드 포함

        Returns:
            QuizSessionResponse
        """
        session_id = str(uuid4())
        started_at = datetime.now(UTC)

        # 카드 가져오기
        cards = await QuizService.get_cards_for_quiz(
            session=session,
            user_id=user_id,
            quiz_type=quiz_type,
            limit=cards_limit,
            include_new=include_new,
            include_review=include_review,
        )

        # 퀴즈 카드 포맷팅
        quiz_cards: list[QuizCard] = []

        for card in cards:
            quiz_card: QuizCard | None = None

            if quiz_type == QuizType.WORD_TO_MEANING:
                quiz_card = await QuizService.format_as_word_to_meaning(session, card)
            elif quiz_type == QuizType.MEANING_TO_WORD:
                quiz_card = await QuizService.format_as_meaning_to_word(session, card)
            elif quiz_type == QuizType.CLOZE:
                quiz_card = await QuizService.format_as_cloze(session, card)
            elif quiz_type == QuizType.LISTENING:
                quiz_card = await QuizService.format_as_listening(session, card)

            if quiz_card:
                quiz_cards.append(quiz_card)

        return QuizSessionResponse(
            session_id=session_id,
            quiz_type=quiz_type,
            total_cards=len(quiz_cards),
            cards=quiz_cards,
            started_at=started_at,
        )

    @staticmethod
    def check_answer(
        card_id: int,
        user_answer: str,
        correct_answer: str,
        quiz_type: QuizType,
    ) -> AnswerResult:
        """
        사용자 답변을 채점합니다.

        Args:
            card_id: 카드 ID
            user_answer: 사용자 입력 답
            correct_answer: 정답
            quiz_type: 퀴즈 유형

        Returns:
            AnswerResult
        """
        # 대소문자 무시 비교
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        # 피드백 메시지 생성
        if is_correct:
            feedback = "정답입니다! 🎉"
        else:
            if quiz_type == QuizType.WORD_TO_MEANING:
                feedback = f"틀렸습니다. 정답: {correct_answer}"
            elif quiz_type == QuizType.MEANING_TO_WORD:
                feedback = f"틀렸습니다. 정답: {correct_answer}"
            elif quiz_type == QuizType.CLOZE:
                feedback = f"빈칸에 들어갈 단어는 '{correct_answer}'입니다."
            else:  # LISTENING
                feedback = f"들은 단어는 '{correct_answer}'입니다."

        return AnswerResult(
            card_id=card_id,
            is_correct=is_correct,
            correct_answer=correct_answer,
            user_answer=user_answer,
            feedback=feedback,
        )
