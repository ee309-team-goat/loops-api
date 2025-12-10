"""
Cloze 문장 생성 서비스.

예문에서 target word를 찾아 빈칸으로 치환하여 cloze 문제를 생성합니다.
"""

import re

from app.models import ClozeQuestion, VocabularyCard


class ClozeService:
    """Cloze 문장 생성 서비스."""

    # 빈칸 표시 문자열
    BLANK = "_____"

    # 일반적인 영어 단어 변형 접미사
    SUFFIXES = [
        "ing",
        "ed",
        "s",
        "es",
        "er",
        "est",
        "ly",
        "tion",
        "sion",
        "ness",
        "ment",
        "ity",
        "ous",
        "ive",
        "al",
        "ful",
        "less",
        "able",
        "ible",
    ]

    @staticmethod
    def _get_word_pattern(word: str) -> re.Pattern:
        """
        단어와 그 변형을 매칭하는 정규식 패턴을 생성합니다.

        예: "contract" → contracts, contracted, contracting 등 매칭
        """
        # 기본 단어 패턴
        base = re.escape(word.lower())

        # 변형 패턴 (접미사 추가)
        suffix_pattern = "|".join(ClozeService.SUFFIXES)

        # 단어 경계를 포함한 패턴
        # 원형 또는 변형된 형태 매칭
        pattern = rf"\b({base}(?:{suffix_pattern})?)\b"

        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    def generate_cloze(
        word: str,
        sentence: str,
        hint: str | None = None,
        audio_url: str | None = None,
    ) -> ClozeQuestion | None:
        """
        예문에서 단어를 찾아 빈칸으로 치환합니다.

        Args:
            word: 정답 단어 (예: "contract")
            sentence: 예문 (예: "The company signed a contract with the supplier.")
            hint: 힌트 (예: "계약")
            audio_url: 오디오 URL (선택)

        Returns:
            ClozeQuestion 또는 None (단어가 문장에 없는 경우)
        """
        if not word or not sentence:
            return None

        pattern = ClozeService._get_word_pattern(word)
        match = pattern.search(sentence)

        if not match:
            return None

        # 실제 매칭된 단어 (변형 포함)
        matched_word = match.group(1)

        # 빈칸으로 치환 (첫 번째 매칭만)
        cloze_sentence = pattern.sub(ClozeService.BLANK, sentence, count=1)

        return ClozeQuestion(
            sentence=cloze_sentence,
            answer=matched_word.lower(),
            hint=hint,
            audio_url=audio_url,
        )

    @staticmethod
    def generate_cloze_from_examples(
        word: str,
        example_sentences: list[dict] | None,
        korean_meaning: str | None = None,
        audio_url: str | None = None,
        max_count: int = 3,
    ) -> list[ClozeQuestion]:
        """
        예문 목록에서 cloze 문장들을 생성합니다.

        Args:
            word: 정답 단어
            example_sentences: 예문 목록 [{"en": "...", "ko": "..."}, ...]
            korean_meaning: 한국어 뜻 (힌트용)
            audio_url: 오디오 URL
            max_count: 최대 생성 개수

        Returns:
            ClozeQuestion 목록
        """
        if not example_sentences:
            return []

        cloze_questions = []

        for example in example_sentences[:max_count]:
            sentence = example.get("en", "")
            if not sentence:
                continue

            # 한국어 번역이 있으면 힌트로 사용, 없으면 korean_meaning 사용
            hint = example.get("ko") or korean_meaning

            cloze = ClozeService.generate_cloze(
                word=word,
                sentence=sentence,
                hint=hint,
                audio_url=audio_url,
            )

            if cloze:
                cloze_questions.append(cloze)

        return cloze_questions

    @staticmethod
    def get_or_generate_cloze(
        card: VocabularyCard,
        max_count: int = 3,
    ) -> list[ClozeQuestion]:
        """
        DB에 저장된 cloze_sentences가 있으면 반환, 없으면 실시간 생성합니다.

        Args:
            card: VocabularyCard 인스턴스
            max_count: 최대 반환 개수

        Returns:
            ClozeQuestion 목록
        """
        # 1. DB에 저장된 cloze_sentences가 있는 경우
        if card.cloze_sentences:
            cloze_list = []
            for item in card.cloze_sentences[:max_count]:
                if isinstance(item, dict):
                    cloze_list.append(
                        ClozeQuestion(
                            sentence=item.get("sentence", ""),
                            answer=item.get("answer", card.english_word),
                            hint=item.get("hint"),
                            audio_url=item.get("audio_url") or card.audio_url,
                        )
                    )
            if cloze_list:
                return cloze_list

        # 2. 없으면 실시간 생성
        return ClozeService.generate_cloze_from_examples(
            word=card.english_word,
            example_sentences=card.example_sentences,
            korean_meaning=card.korean_meaning,
            audio_url=card.audio_url,
            max_count=max_count,
        )

    @staticmethod
    def prepare_cloze_for_storage(
        card: VocabularyCard,
        max_count: int = 3,
    ) -> list[dict]:
        """
        DB 저장용 cloze 데이터를 준비합니다.

        Args:
            card: VocabularyCard 인스턴스
            max_count: 최대 생성 개수

        Returns:
            DB 저장용 딕셔너리 목록
        """
        cloze_questions = ClozeService.generate_cloze_from_examples(
            word=card.english_word,
            example_sentences=card.example_sentences,
            korean_meaning=card.korean_meaning,
            audio_url=card.audio_url,
            max_count=max_count,
        )

        return [
            {
                "sentence": cq.sentence,
                "answer": cq.answer,
                "hint": cq.hint,
                "audio_url": cq.audio_url,
            }
            for cq in cloze_questions
        ]
