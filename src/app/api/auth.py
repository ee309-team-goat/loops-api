"""
Authentication endpoints for user registration and login.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.core.security import create_access_token
from app.database import get_session
from app.models.user import User, UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """
    Register a new user.

    Args:
        user_data: User registration data
        session: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If email or username already exists
    """
    # Check if email already exists
    existing_user = await UserService.get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_user = await UserService.get_user_by_username(session, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create user
    user = await UserService.create_user(session, user_data)
    return user


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    """
    Login with username and password.

    Args:
        form_data: OAuth2 form data with username and password
        session: Database session

    Returns:
        Access token and token type

    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = await UserService.authenticate_user(
        session, form_data.username, form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    await UserService.update_last_login(session, user.id)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def get_current_user(
    current_user: CurrentActiveUser,
) -> User:
    """
    Get the current authenticated user.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        Current user
    """
    return current_user
