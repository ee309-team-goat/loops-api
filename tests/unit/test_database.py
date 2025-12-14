"""Tests for database module."""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestGetSession:
    """Tests for get_session dependency."""

    @pytest.mark.asyncio
    async def test_get_session_yields_session(self, mocker):
        """Test that get_session yields a valid session."""
        from app.database import get_session

        # Create mock session
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        # Mock async_session_maker
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_maker.return_value.__aexit__ = AsyncMock(return_value=None)

        mocker.patch("app.database.async_session_maker", mock_session_maker)

        # Use the generator
        async for session in get_session():
            assert session is mock_session

        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_rollback_on_error(self, mocker):
        """Test that get_session rolls back on error."""
        from app.database import get_session

        # Create mock session that raises on commit
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock(side_effect=RuntimeError("DB Error"))
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        # Mock async_session_maker
        mock_session_maker = MagicMock()
        mock_session_maker.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_maker.return_value.__aexit__ = AsyncMock(return_value=None)

        mocker.patch("app.database.async_session_maker", mock_session_maker)

        # Use the generator - should raise but rollback
        with pytest.raises(RuntimeError):
            async for _session in get_session():
                pass  # Exiting triggers commit which raises

        mock_session.rollback.assert_called_once()


class TestInitDb:
    """Tests for init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self, mocker):
        """Test that init_db creates all tables."""
        from app.database import init_db

        # Mock engine
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()

        mock_engine = MagicMock()
        mock_engine.begin = MagicMock(
            return_value=AsyncMock(
                __aenter__=AsyncMock(return_value=mock_conn),
                __aexit__=AsyncMock(return_value=None),
            )
        )

        mocker.patch("app.database.engine", mock_engine)

        await init_db()

        mock_conn.run_sync.assert_called_once()


class TestDatabaseEngineConfig:
    """Tests for database engine configuration."""

    def test_engine_is_created(self):
        """Test that engine is created on module import."""
        from app.database import engine

        assert engine is not None

    def test_async_session_maker_is_created(self):
        """Test that async_session_maker is created on module import."""
        from app.database import async_session_maker

        assert async_session_maker is not None
