import asyncio
import redis.asyncio as aioredis

from datetime import datetime, timedelta, time
from loguru import logger

from app.config.settings import settings

redis_pool = aioredis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True, max_connections=100)


def get_redis_client() -> aioredis.Redis:
    return aioredis.Redis(connection_pool=redis_pool)


def get_seconds_until_1411() -> int:
    """
    Вычисляет количество секунд до ближайшего времени 14:11
    :return: целое число равное количеству секунд до 14:11
    """
    now = datetime.now()

    target_time = now.replace(hour=14, minute=11, second=0, microsecond=0)

    if now >= target_time:
        target_time += timedelta(days=1)

    time_difference = target_time - now
    return int(time_difference.total_seconds())

async def cache_clear():
    """
    Автоматическая очистка кэша ровно в 14:11
    """
    logger.info('[CACHE] Фоновая задача для очистки кэша запущена')
    target_time = time(14, 11)

    while True:
        now = datetime.now()

        if now.hour == target_time.hour and now.minute == target_time.minute:
            try:
                async with get_redis_client() as redis:
                    await redis.flushdb()   # Полный сброс кэша
                    logger.warning('[CACHE] 14:11 - полный сброс кэша')
                await asyncio.sleep(61)
            except Exception as e:
                logger.error(f'[CACHE ERROR] Ошибка при очистке кэша: {e}')

        await asyncio.sleep(30)
