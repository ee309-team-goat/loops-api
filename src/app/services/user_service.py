from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserUpdate


class UserService:
    """Service for user CRUD operations."""

    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            session: Database session
            user_data: User creation data

        Returns:
            Created user
        """
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = get_password_hash(user_data.password)

        user = User(**user_dict)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> User | None:
        """
        Get a user by ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
        """
        Get a user by email.

        Args:
            session: Database session
            email: User email

        Returns:
            User if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
        """
        Get a user by username.

        Args:
            session: Database session
            username: Username

        Returns:
            User if found, None otherwise
        """
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Get a list of users with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        statement = select(User).offset(skip).limit(limit)
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user_id: int,
        user_data: UserUpdate,
    ) -> User | None:
        """
        Update a user.

        Args:
            session: Database session
            user_id: User ID
            user_data: Update data

        Returns:
            Updated user if found, None otherwise
        """
        user = await UserService.get_user(session, user_id)
        if not user:
            return None

        update_dict = user_data.model_dump(exclude_unset=True, exclude={"password"})
        for key, value in update_dict.items():
            setattr(user, key, value)

        # Handle password update separately if provided
        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        user = await UserService.get_user(session, user_id)
        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True

    @staticmethod
    async def authenticate_user(
        session: AsyncSession, username: str, password: str
    ) -> User | None:
        """
        Authenticate a user by username and password.

        Args:
            session: Database session
            username: Username
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        user = await UserService.get_user_by_username(session, username)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def update_last_login(session: AsyncSession, user_id: int) -> User | None:
        """
        Update user's last login timestamp.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Updated user if found, None otherwise
        """
        user = await UserService.get_user(session, user_id)
        if not user:
            return None

        user.last_login_at = datetime.now(timezone.utc)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update_study_streak(
        session: AsyncSession, user_id: int, study_date: datetime
    ) -> User | None:
        """
        Update user's study streak based on study activity.

        Args:
            session: Database session
            user_id: User ID
            study_date: Date of study activity

        Returns:
            Updated user if found, None otherwise
        """
        user = await UserService.get_user(session, user_id)
        if not user:
            return None

        now = datetime.now(timezone.utc)

        # If no previous study date, start streak
        if not user.last_study_date:
            user.current_streak = 1
            user.longest_streak = 1
        else:
            # Calculate days difference
            days_diff = (now.date() - user.last_study_date.date()).days

            if days_diff == 0:
                # Same day, no change to streak
                pass
            elif days_diff == 1:
                # Consecutive day, increment streak
                user.current_streak += 1
                user.longest_streak = max(user.longest_streak, user.current_streak)
            else:
                # Streak broken, reset
                user.current_streak = 1

        user.last_study_date = now
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
