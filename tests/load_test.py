import asyncio
import httpx
import time


BASE_URL = 'http://127.0.0.1:8000/api/v1/trading'
TOTAL_REQUESTS = 200
CONCURRENT_LIMIT = 20


async def send_request(client, request_id):
    start = time.time()
    try:
        response = await client.get(f'{BASE_URL}/results/?oil_id=A106&limit=100')
        duration = time.time() - start
        return response.status_code, duration
    except Exception as e:
        return f'Ошибка: {e}', time.time() - start


async def main():
    print(f'Запуск теста производительности с {TOTAL_REQUESTS} запросов')

    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    limits = httpx.Limits(max_keepalive_connections=None, max_connections=None)

    async with httpx.AsyncClient(limits=limits, timeout=10.0) as client:
        tasks = [send_request(client, semaphore) for _ in range(TOTAL_REQUESTS)]

        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_duration = time.time() - start_time

    statuses = [r[0] for r in results]
    durations = [r[1] for r in results]

    success_count = statuses.count(200)
    avg_time = sum(durations) / len(durations) * 1000

    print('\n==Результат теста производительности==')
    print(f'Отправлено запросов: {TOTAL_REQUESTS}')
    print(f'Успешных ответов: {success_count}')
    print(f'Ошибок: {TOTAL_REQUESTS - success_count}')
    print(f'Среднее время ответа: {avg_time:.2f} мс')
    print(f'Общее время теста: {total_duration:.2f} мс')

if __name__ == '__main__':
    asyncio.run(main())