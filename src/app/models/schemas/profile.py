"""Profile schemas for API request/response models."""

from datetime import date, datetime
from uuid import UUID

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.profile import ProfileBase


class ProfileRead(ProfileBase):
    """프로필 조회 응답 스키마."""

    id: UUID = Field(description="사용자 고유 ID (Supabase Auth ID)")
    current_streak: int = Field(description="현재 연속 학습일 수")
    longest_streak: int = Field(description="최장 연속 학습일 수 (역대 기록)")
    last_study_date: date | None = Field(default=None, description="마지막 학습 날짜")
    select_all_decks: bool = Field(description="전체 덱 선택 여부. true면 모든 공개 덱에서 학습")
    daily_goal: int = Field(description="일일 학습 목표 카드 수")
    timezone: str = Field(description="사용자 타임존 (예: Asia/Seoul)")
    theme: str = Field(description="앱 테마 (light, dark, auto)")
    notification_enabled: bool = Field(description="알림 활성화 여부")
    total_study_time_minutes: int = Field(default=0, description="총 학습 시간 (분)")
    created_at: datetime = Field(description="계정 생성 시간 (UTC)")
    updated_at: datetime | None = Field(default=None, description="계정 정보 최종 수정 시간 (UTC)")


class ProfileUpdate(SQLModel):
    """프로필 정보 수정 스키마. 부분 업데이트 지원."""

    select_all_decks: bool | None = Field(default=None, description="전체 덱 선택 여부")
    daily_goal: int | None = Field(
        default=None, gt=0, le=1000, description="일일 학습 목표 (1~1000)"
    )
    timezone: str | None = Field(default=None, max_length=50, description="타임존 (예: Asia/Seoul)")
    theme: str | None = Field(default=None, max_length=20, description="테마 (light, dark, auto)")
    notification_enabled: bool | None = Field(default=None, description="알림 활성화 여부")

    @field_validator("theme")
    @classmethod
    def theme_valid(cls, v: str | None) -> str | None:
        """테마가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v


class DailyGoalRead(SQLModel):
    """일일 목표 조회 응답 스키마."""

    daily_goal: int = Field(description="설정된 일일 목표 카드 수")
    completed_today: int = Field(description="오늘 학습 완료한 카드 수")


class StreakRead(SQLModel):
    """스트릭 정보 조회 응답 스키마."""

    current_streak: int = Field(description="현재 연속 학습일 수")
    longest_streak: int = Field(description="최장 연속 학습일 수 (역대 기록)")
    last_study_date: date | None = Field(default=None, description="마지막 학습 날짜")
    days_studied_this_month: int = Field(description="이번 달 학습한 일수")
    streak_status: str = Field(description="스트릭 상태. 'active'(유지 중) 또는 'broken'(끊김)")
    message: str = Field(description="사용자에게 표시할 동기 부여 메시지")


class ProfileConfigRead(SQLModel):
    """사용자 설정 조회 응답 스키마."""

    daily_goal: int = Field(description="일일 학습 목표 카드 수")
    select_all_decks: bool = Field(description="전체 덱 선택 여부")
    timezone: str = Field(description="사용자 타임존")
    theme: str = Field(description="앱 테마 (light, dark, auto)")
    notification_enabled: bool = Field(description="알림 활성화 여부")


class ProfileConfigUpdate(SQLModel):
    """사용자 설정 수정 스키마. 부분 업데이트 지원."""

    daily_goal: int | None = Field(
        default=None, gt=0, le=1000, description="일일 학습 목표 (1~1000)"
    )
    select_all_decks: bool | None = Field(default=None, description="전체 덱 선택 여부")
    timezone: str | None = Field(default=None, max_length=50, description="타임존 (예: Asia/Seoul)")
    theme: str | None = Field(default=None, max_length=20, description="테마 (light, dark, auto)")
    notification_enabled: bool | None = Field(default=None, description="알림 활성화 여부")

    @field_validator("theme")
    @classmethod
    def theme_valid(cls, v: str | None) -> str | None:
        """테마가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v


class ProfileLevelRead(SQLModel):
    """사용자 레벨 조회 응답 스키마."""

    level: float = Field(description="숙련도 레벨 (1.0 ~ 10.0)")
    cefr_equivalent: str = Field(description="CEFR 등급 (A1, A2, B1, B2, C1, C2)")
    total_reviews: int = Field(description="총 복습 횟수")
    accuracy_rate: float = Field(description="전체 정확도 (%)")
    mastered_cards: int = Field(description="마스터한 카드 수 (REVIEW 상태)")
