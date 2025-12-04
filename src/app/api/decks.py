"""
Deck-related API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import DecksListResponse
from app.services.deck_service import DeckService

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("", response_model=DecksListResponse)
async def get_decks_list(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
) -> DecksListResponse:
    """
    Get list of all accessible decks with progress information.

    Returns public decks and user's own decks with learning progress statistics.
    """
    return await DeckService.get_decks_list(session, current_user.id, skip, limit)
