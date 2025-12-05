from datetime import UTC, date, datetime, timedelta

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, UserCardProgress, UserUpdate


class UserService:
    """Service for user CRUD operations."""

    @staticmethod
    async def create_user(
        session: AsyncSession,
        supabase_uid: str,
        email: str,
        username: str,
    ) -> User:
        """Create a new user linked to Supabase Auth."""
        user = User(
            supabase_uid=supabase_uid,
            email=email,
            username=username,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> User | None:
        """Get a user by ID."""
        return await session.get(User, user_id)

    @staticmethod
    async def get_user_by_supabase_uid(session: AsyncSession, supabase_uid: str) -> User | None:
        """Get a user by Supabase UID."""
        statement = select(User).where(User.supabase_uid == supabase_uid)
        result = await session.exec(statement)
        return result.one_or_none()

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
        """Get a user by email."""
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.one_or_none()

    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
        """Get a user by username."""
        statement = select(User).where(User.username == username)
        result = await session.exec(statement)
        return result.one_or_none()

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user_id: int,
        user_data: UserUpdate,
    ) -> User | None:
        """Update a user."""
        user = await UserService.get_user(session, user_id)
        if not user:
            return None

        update_dict = user_data.model_dump(exclude_unset=True)
        user.sqlmodel_update(update_dict)

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int) -> bool:
        """Delete a user."""
        user = await UserService.get_user(session, user_id)
        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True

    @staticmethod
    async def get_daily_goal(session: AsyncSession, user_id: int) -> dict:
        """Get the user's daily goal and today's completion count."""
        user = await UserService.get_user(session, user_id)
        if not user:
            return None

        # Count today's reviews from UserCardProgress
        today = datetime.now(UTC).date()
        statement = select(func.count(UserCardProgress.id)).where(
            UserCardProgress.user_id == user_id,
            func.date(UserCardProgress.last_review_date) == today,
        )
        result = await session.exec(statement)
        completed_today = result.one()

        return {"daily_goal": user.daily_goal, "completed_today": completed_today}

    @staticmethod
    async def update_user_streak(session: AsyncSession, user_id: int) -> dict:
        """
        Update user streak when study session completes.

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
        user = await session.get(User, user_id)
        if not user:
            return None

        today = date.today()

        # 1. Check if already studied today (same day multiple sessions)
        if user.last_study_date == today:
            return {
                "current_streak": user.current_streak,
                "longest_streak": user.longest_streak,
                "is_new_record": False,
                "streak_status": "continued",
            }

        # 2. Calculate streak
        if user.last_study_date is None:
            # First time studying
            user.current_streak = 1
            streak_status = "started"
        elif user.last_study_date == today - timedelta(days=1):
            # Studied yesterday - continue streak
            user.current_streak += 1
            streak_status = "continued"
        else:
            # Gap > 1 day - streak broken, start fresh
            user.current_streak = 1
            streak_status = "broken"

        # 3. Update longest streak if new record
        is_new_record = False
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
            is_new_record = True

        # 4. Update last study date
        user.last_study_date = today

        # 5. Save to database
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "is_new_record": is_new_record,
            "streak_status": streak_status,
        }
