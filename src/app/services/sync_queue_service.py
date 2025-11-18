from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.sync_queue import SyncQueue, SyncQueueCreate, SyncQueueUpdate


class SyncQueueService:
    """Service for sync queue CRUD operations."""

    @staticmethod
    async def enqueue_operation(
        session: AsyncSession, queue_data: SyncQueueCreate
    ) -> SyncQueue:
        """
        Add a new operation to the sync queue.

        Args:
            session: Database session
            queue_data: Sync queue creation data

        Returns:
            Created sync queue entry
        """
        queue_entry = SyncQueue(**queue_data.model_dump())
        session.add(queue_entry)
        await session.commit()
        await session.refresh(queue_entry)
        return queue_entry

    @staticmethod
    async def get_queue_entry(
        session: AsyncSession, queue_id: int
    ) -> SyncQueue | None:
        """
        Get a sync queue entry by ID.

        Args:
            session: Database session
            queue_id: Queue entry ID

        Returns:
            Sync queue entry if found, None otherwise
        """
        statement = select(SyncQueue).where(SyncQueue.id == queue_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_pending_operations(
        session: AsyncSession, user_id: int, limit: int = 100
    ) -> list[SyncQueue]:
        """
        Get pending sync operations for a user.

        Args:
            session: Database session
            user_id: User ID
            limit: Maximum number of operations to return

        Returns:
            List of pending sync queue entries
        """
        statement = (
            select(SyncQueue)
            .where(
                SyncQueue.user_id == user_id,
                SyncQueue.is_synced == 0,
                SyncQueue.retry_count < SyncQueue.max_retries,
            )
            .order_by(SyncQueue.created_at)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def get_failed_operations(
        session: AsyncSession, user_id: int, limit: int = 100
    ) -> list[SyncQueue]:
        """
        Get failed sync operations for a user.

        Args:
            session: Database session
            user_id: User ID
            limit: Maximum number of operations to return

        Returns:
            List of failed sync queue entries
        """
        statement = (
            select(SyncQueue)
            .where(SyncQueue.user_id == user_id, SyncQueue.is_synced == 2)
            .order_by(SyncQueue.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def mark_synced(
        session: AsyncSession, queue_id: int
    ) -> SyncQueue | None:
        """
        Mark a sync operation as successfully synced.

        Args:
            session: Database session
            queue_id: Queue entry ID

        Returns:
            Updated sync queue entry if found, None otherwise
        """
        queue_entry = await SyncQueueService.get_queue_entry(session, queue_id)
        if not queue_entry:
            return None

        queue_entry.is_synced = 1  # 1 = synced
        queue_entry.synced_at = datetime.now(timezone.utc)
        session.add(queue_entry)
        await session.commit()
        await session.refresh(queue_entry)
        return queue_entry

    @staticmethod
    async def mark_failed(
        session: AsyncSession, queue_id: int, error_message: str
    ) -> SyncQueue | None:
        """
        Mark a sync operation as failed.

        Args:
            session: Database session
            queue_id: Queue entry ID
            error_message: Error message

        Returns:
            Updated sync queue entry if found, None otherwise
        """
        queue_entry = await SyncQueueService.get_queue_entry(session, queue_id)
        if not queue_entry:
            return None

        queue_entry.is_synced = 2  # 2 = failed
        queue_entry.error_message = error_message
        session.add(queue_entry)
        await session.commit()
        await session.refresh(queue_entry)
        return queue_entry

    @staticmethod
    async def increment_retry(
        session: AsyncSession, queue_id: int
    ) -> SyncQueue | None:
        """
        Increment retry count for a sync operation.

        Args:
            session: Database session
            queue_id: Queue entry ID

        Returns:
            Updated sync queue entry if found, None otherwise
        """
        queue_entry = await SyncQueueService.get_queue_entry(session, queue_id)
        if not queue_entry:
            return None

        queue_entry.retry_count += 1

        # If max retries reached, mark as failed
        if queue_entry.retry_count >= queue_entry.max_retries:
            queue_entry.is_synced = 2  # 2 = failed
            queue_entry.error_message = "Max retries exceeded"

        session.add(queue_entry)
        await session.commit()
        await session.refresh(queue_entry)
        return queue_entry

    @staticmethod
    async def update_queue_entry(
        session: AsyncSession, queue_id: int, queue_data: SyncQueueUpdate
    ) -> SyncQueue | None:
        """
        Update a sync queue entry.

        Args:
            session: Database session
            queue_id: Queue entry ID
            queue_data: Update data

        Returns:
            Updated sync queue entry if found, None otherwise
        """
        queue_entry = await SyncQueueService.get_queue_entry(session, queue_id)
        if not queue_entry:
            return None

        update_dict = queue_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(queue_entry, key, value)

        session.add(queue_entry)
        await session.commit()
        await session.refresh(queue_entry)
        return queue_entry

    @staticmethod
    async def delete_queue_entry(session: AsyncSession, queue_id: int) -> bool:
        """
        Delete a sync queue entry.

        Args:
            session: Database session
            queue_id: Queue entry ID

        Returns:
            True if deleted, False if not found
        """
        queue_entry = await SyncQueueService.get_queue_entry(session, queue_id)
        if not queue_entry:
            return False

        await session.delete(queue_entry)
        await session.commit()
        return True
