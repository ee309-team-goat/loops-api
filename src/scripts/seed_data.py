"""
Seed script to populate database with sample data.

This script adds:
- 2 sample users (testuser, kaiststudent)
- 3 sample vocabulary cards (contract, algorithm, challenge)

Automatic frequency rank and CEFR level assignment:
- Uses FrequencyMapper from update_cards_via_api.py
- Uses CEFRMapper from update_cards_via_api.py

Run with: uv run python src/scripts/seed_data.py
"""

import asyncio
import csv
import sys
from pathlib import Path

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash
from app.database import async_session_maker
from app.models.user import User
from app.models.vocabulary_card import VocabularyCard

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


class FrequencyMapper:
    """Handles loading frequency data and mapping to vocabulary cards."""

    UNMATCHED_RANK = 999999
    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "frequency"

    def __init__(self):
        self.frequency_map: dict[str, int] = {}

    def load_coca_data(self) -> dict[str, int]:
        """Load COCA Top 5000 frequency data."""
        file_path = self.DATA_DIR / "COCA_5000.csv"
        frequency_map = {}

        with open(file_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["lemma"].lower().strip()
                rank = int(row["rank"])
                frequency_map[word] = rank

        return frequency_map

    def load_google_ngram_data(self) -> dict[str, int]:
        """Load Google Ngram 246k frequency data."""
        file_path = self.DATA_DIR / "google_ngram_frequency_alpha.txt"
        frequency_map = {}

        with open(file_path, encoding="utf-8") as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    rank_str = parts[0]
                    word = parts[1].lower().strip()
                    try:
                        rank = int(rank_str)
                        frequency_map[word] = rank
                    except ValueError:
                        continue

        return frequency_map

    def load_all_sources(self) -> dict[str, int]:
        """
        Load all sources and merge them with priority.
        Priority: COCA > Google Ngram
        """
        # Start with Google Ngram (lower priority)
        combined = self.load_google_ngram_data()

        # Override with COCA (highest priority)
        coca_map = self.load_coca_data()
        for word, rank in coca_map.items():
            combined[word] = rank

        return combined

    def load_frequency_data(self):
        """Load frequency data from all sources."""
        self.frequency_map = self.load_all_sources()

    def get_rank(self, english_word: str) -> int:
        """
        Get frequency rank for an English word.
        Returns UNMATCHED_RANK (999999) if not found.
        """
        if not english_word or not english_word.strip():
            return self.UNMATCHED_RANK

        import string

        word_lower = english_word.lower().strip()
        word_clean = word_lower.strip(string.punctuation)

        # Try exact match
        if word_clean in self.frequency_map:
            return self.frequency_map[word_clean]

        # Try first word for multi-word phrases
        words = word_clean.split()
        if len(words) > 1:
            first_word = words[0]
            if first_word in self.frequency_map:
                return self.frequency_map[first_word]

        return self.UNMATCHED_RANK


class CEFRMapper:
    """Handles loading CEFR level data and mapping to vocabulary cards."""

    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "frequency"

    def __init__(self):
        self.cefr_map: dict[str, str] = {}

    def load_oxford_data(self):
        """Load Oxford 3000 and 5000 CEFR data."""
        # Load Oxford 3000
        oxford_3000_path = self.DATA_DIR / "oxford-3000.csv"
        with open(oxford_3000_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["word"].lower().strip()
                level = row["level"].upper()
                self.cefr_map[word] = level

        # Load Oxford 5000
        oxford_5000_path = self.DATA_DIR / "oxford-5000.csv"
        with open(oxford_5000_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["word"].lower().strip()
                level = row["level"].upper()
                # Don't override if already set from Oxford 3000
                if word not in self.cefr_map:
                    self.cefr_map[word] = level

    def get_cefr_level_from_frequency(self, frequency_rank: int) -> str:
        """
        Assign CEFR level based on frequency rank.

        Fallback when word not in Oxford data:
        - A1: 1-500 (most common)
        - A2: 501-1500
        - B1: 1501-3000
        - B2: 3001-5000
        - C1: 5001-10000
        - C2: 10001+ (rare)
        """
        if frequency_rank <= 500:
            return "A1"
        elif frequency_rank <= 1500:
            return "A2"
        elif frequency_rank <= 3000:
            return "B1"
        elif frequency_rank <= 5000:
            return "B2"
        elif frequency_rank <= 10000:
            return "C1"
        else:
            return "C2"

    def get_level(self, english_word: str, frequency_rank: int) -> str:
        """
        Get CEFR level for an English word.
        Prioritizes Oxford data, falls back to frequency-based assignment.
        """
        if not english_word or not english_word.strip():
            return self.get_cefr_level_from_frequency(frequency_rank)

        import string

        word_lower = english_word.lower().strip()
        word_clean = word_lower.strip(string.punctuation)

        # Try exact match in Oxford data
        if word_clean in self.cefr_map:
            return self.cefr_map[word_clean]

        # Try first word for multi-word phrases
        words = word_clean.split()
        if len(words) > 1:
            first_word = words[0]
            if first_word in self.cefr_map:
                return self.cefr_map[first_word]

        # Fallback to frequency-based
        return self.get_cefr_level_from_frequency(frequency_rank)


async def seed_users(session: AsyncSession) -> None:
    """Seed sample users."""
    print("Seeding users...")

    # Check if users already exist
    statement = select(User).where(User.email == "test@example.com")
    result = await session.exec(statement)
    if result.one_or_none():
        print("  ⚠️  Users already exist, skipping...")
        return

    # Sample password: "password123" (same hash as in SQL file)
    # You can change this or use individual passwords
    hashed_password = get_password_hash("password123")

    users = [
        User(
            email="test@example.com",
            username="testuser",
            hashed_password=hashed_password,
            full_name="홍길동",
            occupation="IT개발자",
            language_level="intermediate",
            is_active=True,
            is_verified=True,
        ),
        User(
            email="demo@kaist.ac.kr",
            username="kaiststudent",
            hashed_password=hashed_password,
            full_name="김준호",
            occupation="학생",
            language_level="advanced",
            is_active=True,
            is_verified=True,
        ),
    ]

    for user in users:
        session.add(user)
        print(f"  ✅ Added user: {user.username} ({user.email})")

    await session.commit()
    print("✅ Users seeded successfully\n")


async def seed_vocabulary_cards(
    session: AsyncSession, freq_mapper: FrequencyMapper, cefr_mapper: CEFRMapper
) -> None:
    """Seed sample vocabulary cards with automatic frequency rank and CEFR level."""
    print("Seeding vocabulary cards...")

    # Check if cards already exist
    statement = select(VocabularyCard).where(VocabularyCard.word == "contract")
    result = await session.exec(statement)
    if result.one_or_none():
        print("  ⚠️  Vocabulary cards already exist, skipping...")
        return

    # Sample cards without frequency_rank and cefr_level (will be auto-assigned)
    cards_data = [
        {
            "word": "contract",
            "translation": "계약",
            "part_of_speech": "noun",
            "pronunciation_ipa": "/ˈkɑːntrækt/",
            "pronunciation_kr": "칸트랙트",
            "example_sentences": [
                {
                    "en": "I signed a contract with the company.",
                    "kr": "나는 회사와 계약을 체결했다.",
                    "context": "business",
                }
            ],
            "difficulty_level": "intermediate",
            "tags": ["business", "legal"],
        },
        {
            "word": "algorithm",
            "translation": "알고리즘",
            "part_of_speech": "noun",
            "pronunciation_ipa": "/ˈælɡərɪðəm/",
            "pronunciation_kr": "앨거리듬",
            "example_sentences": [
                {
                    "en": "The algorithm improves over time.",
                    "kr": "알고리즘은 시간이 지남에 따라 개선된다.",
                    "context": "IT",
                }
            ],
            "difficulty_level": "advanced",
            "tags": ["IT", "computer science"],
        },
        {
            "word": "challenge",
            "translation": "도전, 과제",
            "part_of_speech": "noun",
            "pronunciation_ipa": "/ˈtʃælɪndʒ/",
            "pronunciation_kr": "챌린지",
            "example_sentences": [
                {
                    "en": "This project is a real challenge.",
                    "kr": "이 프로젝트는 진짜 도전이다.",
                    "context": "general",
                }
            ],
            "difficulty_level": "beginner",
            "tags": ["general", "business"],
        },
    ]

    for card_data in cards_data:
        # Automatically assign frequency rank and CEFR level
        word = card_data["word"]
        frequency_rank = freq_mapper.get_rank(word)
        cefr_level = cefr_mapper.get_level(word, frequency_rank)

        # Create card with auto-assigned values
        card = VocabularyCard(
            **card_data, frequency_rank=frequency_rank, cefr_level=cefr_level
        )

        session.add(card)
        print(
            f"  ✅ Added card: {card.word} (freq: {frequency_rank}, CEFR: {cefr_level})"
        )

    await session.commit()
    print("✅ Vocabulary cards seeded successfully\n")


async def main():
    """Main seeding function."""
    print("\n" + "=" * 50)
    print("DATABASE SEEDING SCRIPT")
    print("=" * 50 + "\n")

    # Initialize frequency and CEFR mappers
    print("Loading frequency and CEFR data...")
    freq_mapper = FrequencyMapper()
    freq_mapper.load_frequency_data()
    print(f"  ✅ Loaded {len(freq_mapper.frequency_map)} frequency mappings")

    cefr_mapper = CEFRMapper()
    cefr_mapper.load_oxford_data()
    print(f"  ✅ Loaded {len(cefr_mapper.cefr_map)} CEFR mappings\n")

    async with async_session_maker() as session:
        try:
            await seed_users(session)
            await seed_vocabulary_cards(session, freq_mapper, cefr_mapper)

            print("=" * 50)
            print("✅ ALL DATA SEEDED SUCCESSFULLY!")
            print("=" * 50)
            print("\nSample credentials:")
            print("  Username: testuser")
            print("  Password: password123")
            print("\n  Username: kaiststudent")
            print("  Password: password123")
            print("\n" + "=" * 50 + "\n")

        except Exception as e:
            print(f"\n❌ Error seeding data: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
