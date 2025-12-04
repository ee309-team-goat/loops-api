"""
Deck-related API endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveUser
from app.database import get_session
from app.models import (
    Deck,
    DecksListResponse,
    DeckWithProgressRead,
    GetSelectedDecksResponse,
    SelectedDeckInfo,
    SelectDecksRequest,
    SelectDecksResponse,
    UserSelectedDeck,
)
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

    # Calculate progress for each deck
    decks_with_progress = []
    for deck in decks:
        progress = await DeckService.calculate_deck_progress(session, current_user.id, deck.id)
        deck_dict = {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description,
            **progress,
        }
        decks_with_progress.append(DeckWithProgressRead(**deck_dict))

    return DecksListResponse(
        decks=decks_with_progress,
        total=total_count,
        skip=skip,
        limit=limit,
    )


@router.put("/selected-decks", response_model=SelectDecksResponse)
async def update_selected_decks(
    request: SelectDecksRequest,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    Update user's selected decks for learning.

    If select_all=true, user will study from all public decks.
    If select_all=false, user will study only from specified deck_ids.
    """
    # Update user's select_all_decks field
    current_user.select_all_decks = request.select_all
    session.add(current_user)

    # Clear existing selections
    delete_stmt = delete(UserSelectedDeck).where(UserSelectedDeck.user_id == current_user.id)
    await session.exec(delete_stmt)

    selected_deck_ids = []

    # If select_all=false, validate and add specific decks
    if not request.select_all:
        if not request.deck_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="deck_ids must be provided when select_all is false",
            )

        # Validate all deck IDs exist and are accessible
        for deck_id in request.deck_ids:
            deck_query = select(Deck).where(
                Deck.id == deck_id,
                (Deck.is_public == True) | (Deck.creator_id == current_user.id),
            )
            result = await session.exec(deck_query)
            deck = result.one_or_none()

            if not deck:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Deck with id {deck_id} not found or not accessible",
                )

        # Add selected decks to user_selected_decks table
        for deck_id in request.deck_ids:
            selected_deck = UserSelectedDeck(
                user_id=current_user.id,
                deck_id=deck_id,
            )
            session.add(selected_deck)

        selected_deck_ids = request.deck_ids

    await session.commit()

    return SelectDecksResponse(
        select_all=request.select_all,
        selected_deck_ids=selected_deck_ids,
    )


@router.get("/selected-decks", response_model=GetSelectedDecksResponse)
async def get_selected_decks(
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_user: CurrentActiveUser = None,
):
    """
    Get user's currently selected decks.

    Returns select_all status and deck details with progress information.
    """
    select_all = current_user.select_all_decks
    deck_ids = []
    decks = []

    # If select_all=false, get selected deck IDs from user_selected_decks table
    if not select_all:
        selected_query = select(UserSelectedDeck).where(
            UserSelectedDeck.user_id == current_user.id
        )
        result = await session.exec(selected_query)
        selected_decks = list(result.all())
        deck_ids = [sd.deck_id for sd in selected_decks]

        # Get deck details with progress for each selected deck
        for deck_id in deck_ids:
            # Get deck
            deck_query = select(Deck).where(Deck.id == deck_id)
            result = await session.exec(deck_query)
            deck = result.one_or_none()

            if deck:
                # Calculate progress
                progress = await DeckService.calculate_deck_progress(
                    session, current_user.id, deck_id
                )

                deck_info = SelectedDeckInfo(
                    id=deck.id,
                    name=deck.name,
                    total_cards=progress["total_cards"],
                    progress_percent=progress["progress_percent"],
                )
                decks.append(deck_info)

    return GetSelectedDecksResponse(
        select_all=select_all,
        deck_ids=deck_ids,
        decks=decks,
    )
