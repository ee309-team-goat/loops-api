"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import verify_supabase_token
from app.database import get_session
from app.models import User
from app.services.user_service import UserService

# HTTPBearer scheme for token extraction from Authorization header
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """
    Get the current authenticated user from Supabase JWT token.

    Args:
        credentials: Bearer token from Authorization header
        session: Database session

    Returns:
        User object of authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify Supabase JWT
    payload = verify_supabase_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    # Extract supabase user id from token
    supabase_uid: str = payload.get("sub")
    if supabase_uid is None:
        raise credentials_exception

    # Get user from database by supabase_uid
    user = await UserService.get_user_by_supabase_uid(session, supabase_uid)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current active user.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User object if active

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
