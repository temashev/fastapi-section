import pytest

from unittest.mock import AsyncMock, MagicMock
from datetime import date

from app.crud import TradingRepository
from app.db.models import SpimexTradingResult

pytestmark = pytest.mark.asyncio


async def test_repository_get_last_dates():
    """
    Тест логики репозитория
    """
    mock_db_session = AsyncMock()

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [date(2026, 6, 19), date(2026, 6, 18)]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db_session.execute.return_value = mock_result

    repo = TradingRepository(db=mock_db_session)

    result = await repo.get_last_dates(last_days=2)

    mock_db_session.execute.assert_called_once()

    assert len(result) == 2
    assert result[0] == date(2026, 6, 19)
