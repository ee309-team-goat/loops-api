"""
API routes for all endpoints.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import router as auth_router
from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models.user import User, UserRead, UserUpdate
from app.models.user_card_progress import ReviewRequest, ReviewResponse, UserCardProgressRead
from app.models.vocabulary_card import (
    VocabularyCardCreate,
    VocabularyCardRead,
    VocabularyCardUpdate,
)
from app.services.user_card_progress_service import UserCardProgressService
from app.services.user_service import UserService
from app.services.vocabulary_card_service import VocabularyCardService

router = APIRouter()

# Include auth router
router.include_router(auth_router)


@router.get("/")
async def api_root():
    """API root endpoint."""
    return {"message": "Loops API v1 - Vocabulary Learning System"}


# ============================================================================
# USER ENDPOINTS
# ============================================================================


@router.get("/users/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: CurrentActiveUser,
) -> User:
    """Get the current authenticated user's profile."""
    return current_user


@router.get("/users", response_model=list[UserRead])
async def get_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get a list of users (requires authentication)."""
    users = await UserService.get_users(session, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get a user by ID (requires authentication)."""
    user = await UserService.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Update a user (requires authentication)."""
    # Users can only update their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    user = await UserService.update_user(session, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Delete a user (requires authentication)."""
    # Users can only delete their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    success = await UserService.delete_user(session, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return None


# ============================================================================
# VOCABULARY CARD ENDPOINTS
# ============================================================================


@router.post("/cards", response_model=VocabularyCardRead, status_code=status.HTTP_201_CREATED)
async def create_vocabulary_card(
    card_data: VocabularyCardCreate,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Create a new vocabulary card (requires authentication)."""
    card = await VocabularyCardService.create_card(session, card_data)
    return card


@router.get("/cards", response_model=list[VocabularyCardRead])
async def get_vocabulary_cards(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    difficulty_level: Optional[str] = Query(default=None),
    deck_id: Optional[int] = Query(default=None),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get a list of vocabulary cards with optional filters (requires authentication)."""
    cards = await VocabularyCardService.get_cards(
        session, skip=skip, limit=limit, difficulty_level=difficulty_level, deck_id=deck_id
    )
    return cards


@router.get("/cards/search", response_model=list[VocabularyCardRead])
async def search_vocabulary_cards(
    q: str = Query(..., min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Search vocabulary cards by word or translation (requires authentication)."""
    cards = await VocabularyCardService.search_cards(session, q, skip=skip, limit=limit)
    return cards


@router.get("/cards/{card_id}", response_model=VocabularyCardRead)
async def get_vocabulary_card(
    card_id: int,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get a vocabulary card by ID (requires authentication)."""
    card = await VocabularyCardService.get_card(session, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found",
        )
    return card


@router.patch("/cards/{card_id}", response_model=VocabularyCardRead)
async def update_vocabulary_card(
    card_id: int,
    card_data: VocabularyCardUpdate,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Update a vocabulary card (requires authentication)."""
    card = await VocabularyCardService.update_card(session, card_id, card_data)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found",
        )
    return card


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vocabulary_card(
    card_id: int,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Delete a vocabulary card (requires authentication)."""
    success = await VocabularyCardService.delete_card(session, card_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found",
        )
    return None


# ============================================================================
# PROGRESS / REVIEW ENDPOINTS (FSRS)
# ============================================================================


@router.post("/progress/review", response_model=UserCardProgressRead)
async def submit_card_review(
    review_data: ReviewRequest,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    Submit a card review using FSRS algorithm.

    Rating values:
    - 1: Again (forgot)
    - 2: Hard (difficult to recall)
    - 3: Good (recalled with effort)
    - 4: Easy (perfect recall)
    """
    try:
        progress = await UserCardProgressService.process_review(
            session, current_user.id, review_data.card_id, review_data.rating
        )

        # Update study streak
        await UserService.update_study_streak(session, current_user.id, progress.last_review_date)

        return progress
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/progress/due", response_model=list[UserCardProgressRead])
async def get_due_cards(
    limit: int = Query(default=20, ge=1, le=100),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get cards due for review (requires authentication)."""
    cards = await UserCardProgressService.get_due_cards(session, current_user.id, limit=limit)
    return cards


@router.get("/progress/new", response_model=list[UserCardProgressRead])
async def get_new_cards(
    limit: int = Query(default=20, ge=1, le=100),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get new cards to learn (requires authentication)."""
    cards = await UserCardProgressService.get_new_cards(session, current_user.id, limit=limit)
    return cards


@router.get("/progress/statistics")
async def get_progress_statistics(
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get user's progress statistics (requires authentication)."""
    stats = await UserCardProgressService.get_progress_statistics(session, current_user.id)
    return stats


@router.get("/progress/{card_id}", response_model=UserCardProgressRead)
async def get_card_progress(
    card_id: int,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get progress for a specific card (requires authentication)."""
    progress = await UserCardProgressService.get_user_card_progress(
        session, current_user.id, card_id
    )
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this card",
        )
    return progress
