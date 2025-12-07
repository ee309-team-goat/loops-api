"""사용자 선택 덱 관련 스키마."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class UserSelectedDeckCreate(SQLModel):
    """사용자 선택 덱 생성 스키마."""

    user_id: int = Field(description="사용자 ID")
    deck_id: int = Field(description="덱 ID")


class UserSelectedDeckRead(SQLModel):
    """사용자 선택 덱 조회 응답 스키마."""

    id: int = Field(description="선택 기록 고유 ID")
    user_id: int = Field(description="사용자 ID")
    deck_id: int = Field(description="덱 ID")
    created_at: datetime = Field(description="선택 시간 (UTC)")
    updated_at: datetime | None = Field(default=None, description="최종 수정 시간 (UTC)")


class SelectDecksRequest(SQLModel):
    """학습 덱 선택 요청 스키마."""

    select_all: bool = Field(
        description="전체 덱 선택 여부. true면 모든 공개 덱에서 학습, false면 deck_ids에 지정된 덱만"
    )
    deck_ids: list[int] | None = Field(
        default=None,
        description="선택할 덱 ID 목록. select_all=false일 때 필수. 예: [1, 2, 3]",
    )


class SelectDecksResponse(SQLModel):
    """학습 덱 선택 응답 스키마."""

    select_all: bool = Field(description="전체 덱 선택 여부")
    selected_deck_ids: list[int] = Field(
        description="선택된 덱 ID 목록 (select_all=true면 빈 배열)"
    )


class SelectedDeckInfo(SQLModel):
    """선택된 덱 정보 스키마."""

    id: int = Field(description="덱 고유 ID")
    name: str = Field(description="덱 이름")
    total_cards: int = Field(description="덱 내 총 카드 수")
    progress_percent: float = Field(description="학습 진행률 (%)")


class GetSelectedDecksResponse(SQLModel):
    """선택된 덱 조회 응답 스키마."""

    select_all: bool = Field(description="전체 덱 선택 여부")
    deck_ids: list[int] = Field(description="선택된 덱 ID 목록 (select_all=true면 빈 배열)")
    decks: list[SelectedDeckInfo] = Field(
        description="선택된 덱의 상세 정보 목록 (select_all=true면 빈 배열)"
    )
