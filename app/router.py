import json
import hashlib

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any
from datetime import date

from app.db.cache import get_redis_client, get_seconds_until_1411
from app.db.database import get_db_session
from app.schemas import TradingDateResponse, TradingDynamicsResponse
from app.crud import TradingRepository
from app.logging.logger import logger

router = APIRouter(prefix='/api/v1/trading', tags=['Trading'])


def serialize_item(item: Any) -> dict:
    """
    Трансформирует ORM в JSON
    :param item:
    :return:
    """
    if hasattr(item.date, 'strftime'):
        formatted_date = item.date.strftime('%Y-%m-%d')
    else:
        formatted_date = str(item.date)

    return {
        'id': item.id,
        'exchange_product_id': item.exchange_product_id,
        'exchange_product_name': item.exchange_product_name,
        'oil_id': item.oil_id,
        'delivery_type_id': item.delivery_type_id,
        'delivery_basis_id': item.delivery_basis_id,
        'delivery_basis_name': item.delivery_basis_name,
        'volume': int(item.volume),
        'total': int(item.total),
        'count': int(item.count),
        'date': formatted_date
    }


async def get_cache(cache_key: str, coro, **kwargs) -> List[dict]:
    """
    Ищет кэш в Redis, а если его нет, то выполняет корутину и сохраняет ее результат
    :param cache_key: ключ кэширования
    :param coro: выполняемая корутина
    :return: кэшированный результат работы корутины
    """
    redis = get_redis_client()

    try:
        cached_data = await redis.get(cache_key)
        if cached_data:
            logger.info(f'[CACHE HIT] Возвращен Кэш для {cache_key}')
            return json.loads(cached_data)

        logger.info(f'[CACHE MISS] Данные не закэшированы. Запрос к бд для {cache_key}')
        data = await coro(**kwargs)

        if data and isinstance(data[0], date):
            response_data = [{'date': d.strftime('%Y-%m-%dT%H:%M:%S')} for d in data]
        else:
            response_data = [serialize_item(item) for item in data]

        ttl = get_seconds_until_1411()
        await redis.set(cache_key, json.dumps(response_data), ex=ttl)
        logger.info(f'[CACHE SET] Данные закэшированы с TTL: {ttl} сек. для ключа {cache_key}')

        return response_data

    except Exception as e:
        import traceback
        logger.error(f'[CACHE ERROR] Ошибка кэша: {e}')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        await redis.close()


@router.get('/dates/', response_model=List[TradingDateResponse])
async def read_last_trading_dates(
        last_days: int = Query(default=30, ge=1),
        db: AsyncSession = Depends(get_db_session)
) -> list:
    """
    Отдает список дат последних торговых дней
    :param last_days: количество торговых дней
    :param db: сессия БД
    :return: список дат последних торговых дней
    """
    cache_key = f'trading:dates:last_days:{last_days}'
    repo = TradingRepository(db)
    return await get_cache(cache_key=cache_key, coro=repo.get_last_dates, last_days=last_days)


@router.get('/dynamics/', response_model=List[TradingDynamicsResponse])
async def read_trading_dynamics(
        start_date: date = Query(...), end_date: date = Query(...), oil_id: Optional[str] = Query(None),
        delivery_type_id: Optional[str] = Query(None), delivery_basis_id: Optional[str] = Query(None),
        db: AsyncSession = Depends(get_db_session)
):
    """
    Отдает динамику торгов за указанный период
    :param start_date: Начальная дата периода
    :param end_date: Конечная дата периода
    :param oil_id: Идентификатор нефтяного продукта
    :param delivery_type_id: Тип поставки
    :param delivery_basis_id: Базис поставки
    :param db: сессия БД
    :return: список объектов TradingDynamicsResponse
    """
    params = f'{start_date}:{end_date}:{oil_id}:{delivery_type_id}:{delivery_basis_id}'
    params_hash = hashlib.md5(params.encode('utf-8')).hexdigest()
    cache_key = f'trading:dynamics:{params_hash}'

    repo = TradingRepository(db)

    return await get_cache(
        cache_key=cache_key, coro=repo.get_dynamics, start_date=start_date, end_date=end_date, oil_id=oil_id,
        delivery_basis_id=delivery_basis_id, delivery_type_id=delivery_type_id
    )


@router.get('/results/', response_model=List[TradingDynamicsResponse])
async def read_trading_results(
        oil_id: Optional[str] = Query(None), delivery_type_id: Optional[str] = Query(None),
        delivery_basis_id: Optional[str] = Query(None), db: AsyncSession = Depends(get_db_session),
        limit: int = Query(default=100, ge=1, le=1000)
):
    """
    Отдает список последних торгов с указанными фильтрами
    :param oil_id: Идентификатор нефтяного продукта
    :param delivery_type_id: Тип поставки
    :param delivery_basis_id: Базис поставки
    :param db: сессия БД
    :param limit: Максимальное количество результатов (по умолчанию: 100, максимум: 1000)
    :return: список последних торгов, подходящих под фильтры
    """
    params_string = f"{oil_id}:{delivery_type_id}:{delivery_basis_id}:{limit}"
    params_hash = hashlib.md5(params_string.encode('utf-8')).hexdigest()
    cache_key = f"trading:results:{params_hash}"

    repo = TradingRepository(db)

    return await get_cache(
        cache_key=cache_key, coro=repo.get_results, oil_id=oil_id, delivery_type_id=delivery_type_id,
        delivery_basis_id=delivery_basis_id, limit=limit
    )


@router.get('/health/')
async def health_check():
    """
    Эндпоинт для мониторинга состояния сервиса
    :return:
    """
    return {'status': 'healthy'}
