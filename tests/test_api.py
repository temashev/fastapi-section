## TODO: взять schema из прошлого проекта для тестов
import pytest

from fastapi import FastAPI
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app

pytestmark = pytest.mark.asyncio


@patch('app.db.cache.get_redis_client')
async def test_health_check(mock_get_redis):
    """
    Тест для проверки работоспособности
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.get('/api/v1/trading/health/')

    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}


@patch('app.router.get_redis_client')
async def test_cache_hit(mock_get_redis_client):
    """
    Тест логики кеширования. Если данные есть в Redis, то cache hit
    """
    mock_redis = AsyncMock()
    mock_redis.get.return_value = (
        '[{"id": 1, "exchange_product_id": "A106NPT005A", "exchange_product_name": "Бензин (АИ-100-К5) EURO-6, ТАНЕКО (самовывоз", '
        '"oil_id": "A106", "delivery_type_id": "A", "delivery_basis_id": "NPT", "delivery_basis_name": "ТАНЕКО", '
        '"volume": 100, "total": 500000, "count": 5, "date": "2026-06-19"}]'
    )
    mock_get_redis_client.return_value = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        response = await ac.get('/api/v1/trading/results/?oil_id=A106&limit=100')

    assert response.status_code == 200

    mock_redis.get.assert_called_once()

    assert response.json()[0]['id'] == 1


@patch('app.router.get_redis_client')
async def test_cache_miss(mock_get_redis_client):
    """
    Тест логики кеширования. Если данных нет в Redis, то cache miss
    """
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_get_redis_client.return_value = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        try:
            response = await ac.get('/api/v1/trading/dates/?last_days=5')
        except Exception:
            pass

    mock_redis.get.assert_called_once()
