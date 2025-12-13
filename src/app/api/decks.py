"""
덱(단어장) 관련 API 엔드포인트.

단어장 목록 조회, 상세 정보, 학습할 덱 선택 등을 관리합니다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.constants.categories import get_all_category_ids, get_category_metadata
from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import (
    CategoriesResponse,
    CategoryDecksResponse,
    CategoryDetail,
    CategoryWithStats,
    Deck,
    DeckDetailRead,
    DeckInCategory,
    DeckRead,
    DecksListResponse,
    DeckWithProgressRead,
    GetSelectedDecksResponse,
    SelectDecksRequest,
    SelectDecksResponse,
    SelectedDeckInfo,
    UserSelectedDeck,
    VocabularyCard,
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


# ============================================================
# Category APIs
# ============================================================


@router.get(
    "/categories",
    response_model=CategoriesResponse,
    summary="카테고리 목록 조회",
    description="모든 카테고리와 각 카테고리별 덱 수, 선택 상태를 반환합니다.",
    responses={
        200: {"description": "카테고리 목록 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_categories(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> CategoriesResponse:
    """
    모든 카테고리 목록을 통계와 함께 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - 카테고리 기본 정보 (id, name, description, icon)
    - 해당 카테고리의 전체 덱 수
    - 해당 카테고리에서 선택된 덱 수
    - selection_state: all(전체 선택), partial(일부 선택), none(미선택)

    **selection_state 계산:**
    - all: 카테고리의 모든 덱이 선택됨
    - partial: 카테고리의 일부 덱만 선택됨
    - none: 카테고리의 덱이 하나도 선택되지 않음
    """
    categories_list = []

    # Get user's selected deck IDs
    selected_decks_query = select(UserSelectedDeck.deck_id).where(
        UserSelectedDeck.user_id == current_profile.id
    )
    result = await session.exec(selected_decks_query)
    selected_deck_ids = set(result.all())

    for category_id in get_all_category_ids():
        metadata = get_category_metadata(category_id)
        if not metadata:
            continue

        # Count total decks in this category
        total_query = select(func.count(Deck.id)).where(
            Deck.category == category_id,
            (Deck.is_public == True) | (Deck.creator_id == current_profile.id),  # noqa: E712
        )
        result = await session.exec(total_query)
        total_decks = result.one() or 0

        # Get deck IDs in this category
        decks_query = select(Deck.id).where(
            Deck.category == category_id,
            (Deck.is_public == True) | (Deck.creator_id == current_profile.id),  # noqa: E712
        )
        result = await session.exec(decks_query)
        category_deck_ids = set(result.all())

        # Count selected decks in this category
        selected_in_category = category_deck_ids & selected_deck_ids
        selected_decks = len(selected_in_category)

        # Calculate selection_state
        if total_decks == 0:
            selection_state = "none"
        elif selected_decks == total_decks:
            selection_state = "all"
        elif selected_decks > 0:
            selection_state = "partial"
        else:
            selection_state = "none"

        category_info = CategoryWithStats(
            id=category_id,
            name=metadata["name"],
            description=metadata["description"],
            icon=metadata["icon"],
            total_decks=total_decks,
            selected_decks=selected_decks,
            selection_state=selection_state,
        )
        categories_list.append(category_info)

    return CategoriesResponse(categories=categories_list)


@router.get(
    "/categories/{category_id}",
    response_model=CategoryDecksResponse,
    summary="카테고리별 덱 목록 조회",
    description="특정 카테고리에 속한 모든 덱과 선택 상태를 반환합니다.",
    responses={
        200: {"description": "카테고리별 덱 목록 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "카테고리를 찾을 수 없음"},
    },
)
async def get_category_decks(
    category_id: str = Path(..., description="카테고리 ID (예: exam, textbook)"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> CategoryDecksResponse:
    """
    특정 카테고리에 속한 덱 목록을 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - 카테고리 정보 (id, name, description)
    - 해당 카테고리의 덱 목록
      - 각 덱의 기본 정보 (id, name, description)
      - 각 덱의 총 카드 수
      - 각 덱의 선택 여부 (is_selected)
    - 해당 카테고리의 전체 덱 수
    - 해당 카테고리에서 선택된 덱 수
    """
    # Check if category exists
    metadata = get_category_metadata(category_id)
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )

    # Get user's selected deck IDs
    selected_decks_query = select(UserSelectedDeck.deck_id).where(
        UserSelectedDeck.user_id == current_profile.id
    )
    result = await session.exec(selected_decks_query)
    selected_deck_ids = set(result.all())

    # Get all decks in this category
    decks_query = select(Deck).where(
        Deck.category == category_id,
        (Deck.is_public == True) | (Deck.creator_id == current_profile.id),  # noqa: E712
    )
    result = await session.exec(decks_query)
    decks = list(result.all())

    # Build deck list with is_selected
    decks_list = []
    selected_count = 0

    for deck in decks:
        is_selected = deck.id in selected_deck_ids
        if is_selected:
            selected_count += 1

        cards_query = select(func.count(VocabularyCard.id)).where(VocabularyCard.deck_id == deck.id)
        result = await session.exec(cards_query)
        total_cards = result.one() or 0

        deck_info = DeckInCategory(
            id=deck.id,
            name=deck.name,
            description=deck.description,
            total_cards=total_cards,
            is_selected=is_selected,
        )
        decks_list.append(deck_info)

    category_detail = CategoryDetail(
        id=category_id,
        name=metadata["name"],
        description=metadata["description"],
    )

    return CategoryDecksResponse(
        category=category_detail,
        decks=decks_list,
        total_decks=len(decks),
        selected_decks=selected_count,
    )


@router.put(
    "/categories/{category_id}/select-all",
    status_code=status.HTTP_200_OK,
    summary="카테고리 전체 선택",
    description="특정 카테고리의 모든 덱을 선택합니다.",
    responses={
        200: {"description": "카테고리 전체 선택 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "카테고리를 찾을 수 없음"},
    },
)
async def select_all_category_decks(
    category_id: str = Path(..., description="카테고리 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
):
    """
    특정 카테고리의 모든 덱을 선택합니다.

    **인증 필요:** Bearer 토큰

    **동작:**
    - 해당 카테고리의 모든 덱을 사용자의 selected_decks에 추가
    - 이미 선택된 덱은 건너뜀 (중복 방지)
    """
    # Check if category exists
    metadata = get_category_metadata(category_id)
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )

    # Get all decks in this category
    decks_query = select(Deck.id).where(
        Deck.category == category_id,
        (Deck.is_public == True) | (Deck.creator_id == current_profile.id),  # noqa: E712
    )
    result = await session.exec(decks_query)
    deck_ids = list(result.all())

    # Get already selected decks
    selected_query = select(UserSelectedDeck.deck_id).where(
        UserSelectedDeck.user_id == current_profile.id
    )
    result = await session.exec(selected_query)
    already_selected = set(result.all())

    # Add new selections
    added_count = 0
    for deck_id in deck_ids:
        if deck_id not in already_selected:
            new_selection = UserSelectedDeck(
                user_id=current_profile.id,
                deck_id=deck_id,
            )
            session.add(new_selection)
            added_count += 1

    await session.commit()

    return {
        "message": f"Added {added_count} decks from category '{metadata['name']}'",
        "category_id": category_id,
        "total_decks": len(deck_ids),
        "added_decks": added_count,
    }


@router.delete(
    "/categories/{category_id}/select-all",
    status_code=status.HTTP_200_OK,
    summary="카테고리 전체 선택 해제",
    description="특정 카테고리의 모든 덱 선택을 해제합니다.",
    responses={
        200: {"description": "카테고리 전체 선택 해제 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "카테고리를 찾을 수 없음"},
    },
)
async def deselect_all_category_decks(
    category_id: str = Path(..., description="카테고리 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
):
    """
    특정 카테고리의 모든 덱 선택을 해제합니다.

    **인증 필요:** Bearer 토큰

    **동작:**
    - 해당 카테고리의 모든 덱을 사용자의 selected_decks에서 제거
    """
    # Check if category exists
    metadata = get_category_metadata(category_id)
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id}' not found",
        )

    # Get all deck IDs in this category
    decks_query = select(Deck.id).where(
        Deck.category == category_id,
        (Deck.is_public == True) | (Deck.creator_id == current_profile.id),  # noqa: E712
    )
    result = await session.exec(decks_query)
    deck_ids = list(result.all())

    # Delete selections for these decks
    delete_stmt = delete(UserSelectedDeck).where(
        UserSelectedDeck.user_id == current_profile.id,
        UserSelectedDeck.deck_id.in_(deck_ids),
    )
    result = await session.exec(delete_stmt)
    await session.commit()

    removed_count = result.rowcount

    return {
        "message": f"Removed {removed_count} decks from category '{metadata['name']}'",
        "category_id": category_id,
        "removed_decks": removed_count,
    }
