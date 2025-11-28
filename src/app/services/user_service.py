from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, UserUpdate


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
    async def get_user_by_supabase_uid(
        session: AsyncSession, supabase_uid: str
    ) -> User | None:
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
