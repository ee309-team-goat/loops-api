import enum
from datetime import datetime
from typing import Any, Optional

from sqlmodel import Column, Enum, Field, JSON, SQLModel

from app.models.base import TimestampMixin


class OperationType(str, enum.Enum):
    """Operation type enum for sync queue."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class SyncQueueBase(SQLModel):
    """Base SyncQueue model with shared fields."""

    user_id: int = Field(index=True)
    entity_type: str = Field(max_length=50, index=True)  # "card", "progress", "user_settings"
    entity_id: int = Field(index=True)

    # Sync Status
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    is_synced: bool = Field(default=False, index=True)  # Sync completion status
    error_message: Optional[str] = Field(default=None)
    priority: int = Field(default=0)  # Higher = higher priority


class SyncQueue(SyncQueueBase, table=True):
    """SyncQueue database model for offline sync operations."""

    __tablename__ = "sync_queue"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

    # Operation
    operation: OperationType = Field(sa_column=Column(Enum(OperationType), nullable=False))

    # Payload (Flexible JSON Data)
    # Format: {"field1": "value1", "field2": "value2", ...}
    payload: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    synced_at: Optional[datetime] = Field(default=None)
    last_retry_at: Optional[datetime] = Field(default=None)


class SyncQueueCreate(SyncQueueBase):
    """Schema for creating a sync queue entry."""

    operation: OperationType
    payload: dict[str, Any]


class SyncQueueRead(SyncQueueBase):
    """Schema for reading a sync queue entry."""

    id: int
    operation: OperationType
    payload: dict[str, Any]
    created_at: datetime
    synced_at: Optional[datetime] = None


class SyncQueueUpdate(SQLModel):
    """Schema for updating a sync queue entry."""

    retry_count: Optional[int] = None
    is_synced: Optional[bool] = None
    error_message: Optional[str] = None
    priority: Optional[int] = None
    synced_at: Optional[datetime] = None
    last_retry_at: Optional[datetime] = None
