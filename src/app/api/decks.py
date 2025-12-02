"""
Deck-related API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import Deck, DecksListResponse, DeckWithProgressRead

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("", response_model=DecksListResponse)
async def get_decks_list(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    Get list of all accessible decks with progress information.

    Returns public decks and user's own decks with learning progress statistics.

    TODO: Progress calculation will be implemented in Issue #9 (DeckService).
    Currently returns placeholder values (0) for progress fields.
    """
    # Query for accessible decks (public or created by user)
    decks_query = (
        select(Deck)
        .where((Deck.is_public == True) | (Deck.creator_id == current_user.id))
        .offset(skip)
        .limit(limit)
    )
    result = await session.exec(decks_query)
    decks = list(result.all())

    # Count total accessible decks
    count_query = select(func.count(Deck.id)).where(
        (Deck.is_public == True) | (Deck.creator_id == current_user.id)
    )
    result = await session.exec(count_query)
    total_count = result.one()

    # Build response with placeholder progress values
    # TODO: Replace with actual progress calculation in Issue #9
    decks_with_progress = []
    for deck in decks:
        deck_dict = {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description,
            "total_cards": 0,  # TODO: Calculate in Issue #9
            "learned_cards": 0,  # TODO: Calculate in Issue #9
            "learning_cards": 0,  # TODO: Calculate in Issue #9
            "new_cards": 0,  # TODO: Calculate in Issue #9
            "progress_percent": 0.0,  # TODO: Calculate in Issue #9
        }
        decks_with_progress.append(DeckWithProgressRead(**deck_dict))

    return DecksListResponse(
        decks=decks_with_progress,
        total=total_count,
        skip=skip,
        limit=limit,
    )
