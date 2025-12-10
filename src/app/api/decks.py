"""
덱(단어장) 관련 API 엔드포인트.

단어장 목록 조회, 상세 정보, 학습할 덱 선택 등을 관리합니다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import (
    Deck,
    DeckDetailRead,
    DeckRead,
    DecksListResponse,
    DeckWithProgressRead,
    GetSelectedDecksResponse,
    SelectDecksRequest,
    SelectDecksResponse,
    SelectedDeckInfo,
    UserSelectedDeck,
)
from app.services.deck_service import DeckService

TAG = "decks"
TAG_METADATA = {
    "name": TAG,
    "description": "덱(단어장) 관련 API. 단어장 목록 조회, 상세 정보, 학습할 덱 선택 등을 관리합니다.",
}

router = APIRouter(prefix="/decks", tags=[TAG])


@router.get(
    "",
    response_model=DecksListResponse,
    summary="덱 목록 조회",
    description="접근 가능한 모든 덱 목록을 학습 진행 정보와 함께 반환합니다.",
    responses={
        200: {"description": "덱 목록 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_decks_list(
    skip: int = Query(default=0, ge=0, description="건너뛸 레코드 수 (페이지네이션용)"),
    limit: int = Query(default=10, ge=1, le=100, description="반환할 최대 레코드 수 (1~100)"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> DecksListResponse:
    """
    접근 가능한 덱 목록을 조회합니다.

    **인증 필요:** Bearer 토큰

    **접근 가능한 덱:**
    - 공개 덱 (`is_public: true`)
    - 본인이 생성한 덱

    **반환 정보:**
    - 덱 기본 정보 (ID, 이름, 설명)
    - 학습 진행 상황 (총 카드 수, 학습 완료율)
    - 페이지네이션 정보 (total, skip, limit)

    **쿼리 파라미터:**
    - `skip`: 건너뛸 레코드 수 (기본값: 0)
    - `limit`: 반환할 최대 레코드 수 (기본값: 10, 최대: 100)
    """
    # Query for accessible decks (public or created by user)
    decks_query = (
        select(Deck)
        .where((Deck.is_public == True) | (Deck.creator_id == current_profile.id))  # noqa: E712
        .offset(skip)
        .limit(limit)
    )
    result = await session.exec(decks_query)
    decks = list(result.all())

    # Count total accessible decks
    count_query = select(func.count(Deck.id)).where(
        (Deck.is_public == True) | (Deck.creator_id == current_profile.id)  # noqa: E712
    )
    result = await session.exec(count_query)
    total_count = result.one()

    # Calculate progress for each deck
    decks_with_progress = []
    for deck in decks:
        progress = await DeckService.calculate_deck_progress(session, current_profile.id, deck.id)
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


@router.get(
    "/{deck_id}",
    response_model=DeckDetailRead,
    summary="덱 상세 조회",
    description="특정 덱의 상세 정보와 학습 진행 상황을 조회합니다.",
    responses={
        200: {"description": "덱 상세 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        403: {"description": "권한 없음 - 비공개 덱에 접근 권한이 없음"},
        404: {"description": "덱을 찾을 수 없음"},
    },
)
async def get_deck_detail(
    deck_id: int = Path(description="조회할 덱의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
):
    """
    특정 덱의 상세 정보를 조회합니다.

    **인증 필요:** Bearer 토큰

    **접근 조건:**
    - 공개 덱 (`is_public: true`)
    - 또는 본인이 생성한 덱

    **반환 정보:**
    - 덱 기본 정보: ID, 이름, 설명, 생성자
    - 카드 정보: 총 카드 수
    - 학습 진행: 진행률, 학습/복습 중인 카드 수
    - 생성/수정 시간
    """
    # Get deck
    deck_query = select(Deck).where(Deck.id == deck_id)
    result = await session.exec(deck_query)
    deck = result.one_or_none()

    # Check if deck exists
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with id {deck_id} not found",
        )

    # Check access permission (public or user's own deck)
    if not deck.is_public and deck.creator_id != current_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this deck",
        )

    # Get deck details using DeckRead
    deck_read = DeckRead.model_validate(deck)

    # Calculate progress
    progress = await DeckService.calculate_deck_progress(session, current_profile.id, deck_id)

    # Combine deck details and progress
    response = {
        **deck_read.model_dump(),
        **progress,
    }

    return DeckDetailRead(**response)


@router.put(
    "/selected-decks",
    response_model=SelectDecksResponse,
    summary="학습 덱 선택 설정",
    description="학습에 사용할 덱을 설정합니다. 전체 선택 또는 특정 덱 선택이 가능합니다.",
    responses={
        200: {"description": "덱 선택 설정 성공"},
        400: {"description": "잘못된 요청 - select_all=false인데 deck_ids가 비어있음"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "지정한 덱 ID 중 존재하지 않거나 접근할 수 없는 덱이 있음"},
        422: {"description": "유효성 검사 실패 - 잘못된 데이터 형식"},
    },
)
async def update_selected_decks(
    request: SelectDecksRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
):
    """
    학습에 사용할 덱을 설정합니다.

    **인증 필요:** Bearer 토큰

    **설정 모드:**
    - `select_all: true` → 모든 공개 덱에서 학습
    - `select_all: false` → 지정한 `deck_ids`의 덱에서만 학습

    **요청 본문:**
    - `select_all`: 전체 덱 선택 여부
    - `deck_ids`: 선택할 덱 ID 목록 (select_all=false일 때 필수)

    **주의사항:**
    - `select_all: false`일 때 `deck_ids`는 반드시 제공해야 합니다
    - 존재하지 않거나 접근할 수 없는 덱 ID가 포함되면 404 오류
    """
    # Update profile's select_all_decks field
    current_profile.select_all_decks = request.select_all
    session.add(current_profile)

    # Clear existing selections
    delete_stmt = delete(UserSelectedDeck).where(UserSelectedDeck.user_id == current_profile.id)
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
                (Deck.is_public == True) | (Deck.creator_id == current_profile.id),  # noqa: E712
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
                user_id=current_profile.id,
                deck_id=deck_id,
            )
            session.add(selected_deck)

        selected_deck_ids = request.deck_ids

    await session.commit()

    return SelectDecksResponse(
        select_all=request.select_all,
        selected_deck_ids=selected_deck_ids,
    )


@router.get(
    "/selected-decks",
    response_model=GetSelectedDecksResponse,
    summary="선택된 덱 조회",
    description="현재 학습에 사용하도록 설정된 덱 목록을 조회합니다.",
    responses={
        200: {"description": "선택된 덱 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_selected_decks(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
):
    """
    현재 학습에 사용하도록 설정된 덱을 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `select_all`: 전체 덱 선택 여부
    - `deck_ids`: 선택된 덱 ID 목록 (select_all=false일 때만 의미있음)
    - `decks`: 선택된 덱의 상세 정보 (ID, 이름, 총 카드 수, 진행률)

    **참고:**
    - `select_all: true`인 경우 `deck_ids`와 `decks`는 빈 배열
    """
    select_all = current_profile.select_all_decks
    deck_ids = []
    decks = []

    # If select_all=false, get selected deck IDs from user_selected_decks table
    if not select_all:
        selected_query = select(UserSelectedDeck).where(
            UserSelectedDeck.user_id == current_profile.id
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
                    session, current_profile.id, deck_id
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
