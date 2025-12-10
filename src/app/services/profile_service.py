from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Profile, ProfileUpdate, UserCardProgress, VocabularyCard
from app.models.enums import CardState


class ProfileService:
    """Service for profile CRUD operations."""

    @staticmethod
    async def create_profile(
        session: AsyncSession,
        profile_id: UUID,
    ) -> Profile:
        """Create a new profile linked to Supabase Auth user."""
        profile = Profile(id=profile_id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def get_profile(session: AsyncSession, profile_id: UUID) -> Profile | None:
        """Get a profile by ID (UUID from Supabase Auth)."""
        return await session.get(Profile, profile_id)

    @staticmethod
    async def update_profile(
        session: AsyncSession,
        profile_id: UUID,
        profile_data: ProfileUpdate,
    ) -> Profile | None:
        """Update a profile."""
        profile = await ProfileService.get_profile(session, profile_id)
        if not profile:
            return None

        update_dict = profile_data.model_dump(exclude_unset=True)
        profile.sqlmodel_update(update_dict)

        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def delete_profile(session: AsyncSession, profile_id: UUID) -> bool:
        """Delete a profile."""
        profile = await ProfileService.get_profile(session, profile_id)
        if not profile:
            return False

        await session.delete(profile)
        await session.commit()
        return True

    @staticmethod
    async def get_daily_goal(session: AsyncSession, profile_id: UUID) -> dict | None:
        """Get the user's daily goal and today's completion count."""
        profile = await ProfileService.get_profile(session, profile_id)
        if not profile:
            return None

        # Count today's reviews from UserCardProgress
        today = datetime.now(UTC).date()
        statement = select(func.count(UserCardProgress.id)).where(
            UserCardProgress.user_id == profile_id,
            func.date(UserCardProgress.last_review_date) == today,
        )
        result = await session.exec(statement)
        completed_today = result.one()

        return {"daily_goal": profile.daily_goal, "completed_today": completed_today}

    @staticmethod
    async def update_profile_streak(session: AsyncSession, profile_id: UUID) -> dict | None:
        """
        Update profile streak when study session completes.

        Handles:
        - Same-day multiple sessions (don't double-count)
        - Continue streak if yesterday was studied (+1)
        - Reset streak to 1 if gap > 1 day
        - Update longest_streak if new record
        - Update last_study_date to today

        Returns:
            dict: {
                "current_streak": int,
                "longest_streak": int,
                "is_new_record": bool,
                "streak_status": "continued" | "started" | "broken"
            }
        """
        profile = await session.get(Profile, profile_id)
        if not profile:
            return None

        today = date.today()

        # 1. Check if already studied today (same day multiple sessions)
        if profile.last_study_date == today:
            return {
                "current_streak": profile.current_streak,
                "longest_streak": profile.longest_streak,
                "is_new_record": False,
                "streak_status": "continued",
            }

        # 2. Calculate streak
        if profile.last_study_date is None:
            # First time studying
            profile.current_streak = 1
            streak_status = "started"
        elif profile.last_study_date == today - timedelta(days=1):
            # Studied yesterday - continue streak
            profile.current_streak += 1
            streak_status = "continued"
        else:
            # Gap > 1 day - streak broken, start fresh
            profile.current_streak = 1
            streak_status = "broken"

        # 3. Update longest streak if new record
        is_new_record = False
        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak
            is_new_record = True

        # 4. Update last study date
        profile.last_study_date = today

        # 5. Save to database
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        return {
            "current_streak": profile.current_streak,
            "longest_streak": profile.longest_streak,
            "is_new_record": is_new_record,
            "streak_status": streak_status,
        }

    @staticmethod
    async def calculate_profile_level(session: AsyncSession, profile_id: UUID) -> dict:
        """
        Calculate user's current level based on recent review performance.

        Algorithm:
        1. Get recent 50 reviews (or all if fewer)
        2. Calculate average difficulty of mastered cards (REVIEW state)
        3. Factor in accuracy rate
        4. Map to CEFR level

        Returns:
            dict: {
                "level": float (1.0 - 10.0),
                "cefr_equivalent": str (A1-C2),
                "total_reviews": int,
                "accuracy_rate": float,
                "mastered_cards": int
            }
        """
        # Get recent progress records with card difficulty
        recent_query = (
            select(
                UserCardProgress.difficulty,
                UserCardProgress.card_state,
                UserCardProgress.total_reviews,
                UserCardProgress.correct_count,
                VocabularyCard.cefr_level,
            )
            .select_from(UserCardProgress)
            .join(VocabularyCard, VocabularyCard.id == UserCardProgress.card_id)
            .where(
                UserCardProgress.user_id == profile_id,
                UserCardProgress.total_reviews > 0,
            )
            .order_by(UserCardProgress.last_review_date.desc())
            .limit(50)
        )

        result = await session.exec(recent_query)
        records = result.all()

        if not records:
            return {
                "level": 1.0,
                "cefr_equivalent": "A1",
                "total_reviews": 0,
                "accuracy_rate": 0.0,
                "mastered_cards": 0,
            }

        # Calculate stats
        total_reviews = sum(r[2] for r in records)
        total_correct = sum(r[3] for r in records)
        accuracy_rate = (total_correct / total_reviews * 100) if total_reviews > 0 else 0.0

        # Get mastered cards (REVIEW state) and their difficulties
        mastered = [r for r in records if r[1] == CardState.REVIEW]
        mastered_count = len(mastered)

        # Calculate average difficulty of mastered cards
        if mastered:
            avg_difficulty = sum(r[0] or 5.0 for r in mastered) / len(mastered)
        else:
            # Use all cards if none mastered
            avg_difficulty = sum(r[0] or 5.0 for r in records) / len(records)

        # Apply accuracy weight (higher accuracy = higher effective level)
        accuracy_weight = accuracy_rate / 100.0 if accuracy_rate > 0 else 0.5
        weighted_level = avg_difficulty * (0.7 + 0.3 * accuracy_weight)

        # Clamp to 1.0 - 10.0 range
        level = max(1.0, min(10.0, weighted_level))

        # Map to CEFR level
        cefr_mapping = [
            (2.0, "A1"),
            (3.5, "A2"),
            (5.0, "B1"),
            (6.5, "B2"),
            (8.0, "C1"),
            (10.0, "C2"),
        ]
        cefr_equivalent = "A1"
        for threshold, cefr in cefr_mapping:
            if level <= threshold:
                cefr_equivalent = cefr
                break
        else:
            cefr_equivalent = "C2"

        return {
            "level": round(level, 1),
            "cefr_equivalent": cefr_equivalent,
            "total_reviews": total_reviews,
            "accuracy_rate": round(accuracy_rate, 1),
            "mastered_cards": mastered_count,
        }
