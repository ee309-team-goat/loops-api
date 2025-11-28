from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate


class UserService:
    """Service for user CRUD operations."""

    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user with hashed password."""
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = get_password_hash(user_data.password)

        user = User(**user_dict)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user(session: AsyncSession, user_id: int) -> User | None:
        """Get a user by ID."""
        return await session.get(User, user_id)

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

        update_dict = user_data.model_dump(exclude_unset=True, exclude={"password"})
        user.sqlmodel_update(update_dict)

        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)

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
    async def authenticate_user(
        session: AsyncSession, username: str, password: str
    ) -> User | None:
        """Authenticate a user by username and password."""
        user = await UserService.get_user_by_username(session, username)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
