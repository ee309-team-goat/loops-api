"""
Vocabulary card API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import VocabularyCardCreate, VocabularyCardRead, VocabularyCardUpdate
from app.services.vocabulary_card_service import VocabularyCardService

router = APIRouter(prefix="/cards", tags=["cards"])


@router.post("", response_model=VocabularyCardRead, status_code=status.HTTP_201_CREATED)
async def create_vocabulary_card(
    card_data: VocabularyCardCreate,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Create a new vocabulary card (requires authentication)."""
    card = await VocabularyCardService.create_card(session, card_data)
    return card


@router.get("", response_model=list[VocabularyCardRead])
async def get_vocabulary_cards(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    difficulty_level: str | None = Query(default=None),
    deck_id: int | None = Query(default=None),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """Get a list of vocabulary cards with optional filters (requires authentication)."""
    cards = await VocabularyCardService.get_cards(
        session, skip=skip, limit=limit, difficulty_level=difficulty_level, deck_id=deck_id
    )
    return cards


@router.get("/{card_id}", response_model=VocabularyCardRead)
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


@router.patch("/{card_id}", response_model=VocabularyCardRead)
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


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
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
