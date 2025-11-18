"""
Seed script to populate database with sample data.

This script adds:
- 2 sample users (testuser, kaiststudent)
- 3 sample vocabulary cards (contract, algorithm, challenge)

Run with: uv run python src/scripts/seed_data.py
"""
import asyncio

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash
from app.database import async_session_maker
from app.models.user import User
from app.models.vocabulary_card import VocabularyCard


async def seed_users(session: AsyncSession) -> None:
    """Seed sample users."""
    print("Seeding users...")

    # Check if users already exist
    statement = select(User).where(User.email == "test@example.com")
    result = await session.execute(statement)
    if result.scalar_one_or_none():
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


async def seed_vocabulary_cards(session: AsyncSession) -> None:
    """Seed sample vocabulary cards."""
    print("Seeding vocabulary cards...")

    # Check if cards already exist
    statement = select(VocabularyCard).where(VocabularyCard.word == "contract")
    result = await session.execute(statement)
    if result.scalar_one_or_none():
        print("  ⚠️  Vocabulary cards already exist, skipping...")
        return

    cards = [
        VocabularyCard(
            word="contract",
            translation="계약",
            part_of_speech="noun",
            pronunciation_ipa="/ˈkɑːntrækt/",
            pronunciation_kr="칸트랙트",
            example_sentences=[
                {
                    "en": "I signed a contract with the company.",
                    "kr": "나는 회사와 계약을 체결했다.",
                    "context": "business",
                }
            ],
            difficulty_level="intermediate",
            frequency_rank=1250,
            tags=["business", "legal"],
        ),
        VocabularyCard(
            word="algorithm",
            translation="알고리즘",
            part_of_speech="noun",
            pronunciation_ipa="/ˈælɡərɪðəm/",
            pronunciation_kr="앨거리듬",
            example_sentences=[
                {
                    "en": "The algorithm improves over time.",
                    "kr": "알고리즘은 시간이 지남에 따라 개선된다.",
                    "context": "IT",
                }
            ],
            difficulty_level="advanced",
            frequency_rank=2500,
            tags=["IT", "computer science"],
        ),
        VocabularyCard(
            word="challenge",
            translation="도전, 과제",
            part_of_speech="noun",
            pronunciation_ipa="/ˈtʃælɪndʒ/",
            pronunciation_kr="챌린지",
            example_sentences=[
                {
                    "en": "This project is a real challenge.",
                    "kr": "이 프로젝트는 진짜 도전이다.",
                    "context": "general",
                }
            ],
            difficulty_level="beginner",
            frequency_rank=800,
            tags=["general", "business"],
        ),
    ]

    for card in cards:
        session.add(card)
        print(f"  ✅ Added card: {card.word} ({card.difficulty_level})")

    await session.commit()
    print("✅ Vocabulary cards seeded successfully\n")


async def main():
    """Main seeding function."""
    print("\n" + "=" * 50)
    print("DATABASE SEEDING SCRIPT")
    print("=" * 50 + "\n")

    async with async_session_maker() as session:
        try:
            await seed_users(session)
            await seed_vocabulary_cards(session)

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
