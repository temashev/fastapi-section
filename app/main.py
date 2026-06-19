import asyncio
import time

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from app.db.cache import redis_pool, get_redis_client, cache_clear
from app.router import router
from app.logging.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('[START] Запуск приложения и Redis')

    redis_client = get_redis_client()
    try:
        await redis_client.ping()
        logger.info('[START] Redis подключен')
    except Exception as e:
        logger.error(f'[START] Не удалось подключить Redis: {e}')
    finally:
        await redis_client.close()

    # Создание фонового таска для очисти кэша
    task = asyncio.create_task(cache_clear())

    yield

    task.cancel()

    logger.info('[FINISH] Закрытие Redis...')
    await redis_pool.disconnect()
    logger.info('[FINISH] Redis успешно закрыт.')


app = FastAPI(title='Spimex Trading API', version='1.0.0', lifespan=lifespan)


@app.get('/')
async def root():
    return {'message': 'Spimex Trading API'}


@app.middleware('http')
async def log_requests(request: Request, call_next):
    """
    Мидлвейр для логирования и замера времени
    :param request:
    :param call_next:
    :return:
    """
    start_time = time.time()

    method = request.method
    url = request.url.path
    host = request.client.host if request.client else 'unknown'

    logger.info(f'Запрос: {method} {url} от {host}')

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        logger.info(f'Запрос выполнен: {method} {url}, статус {response.status_code}, время: {process_time:.2f} мс')
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(f'Запрос не выполнен: {method} {url}, ошибка: {e}, время: {process_time:.2f} мс')
        raise


app.include_router(router)
