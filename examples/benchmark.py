import asyncio
import logging
import time

from pymoex import MoexClient

# Включаем логирование, чтобы видеть паузы между запросами
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def run_benchmark():
    async with MoexClient() as client:
        # Список тикеров для теста (можно дублировать, чтобы проверить кэш)
        tickers = ["SBER", "GAZP", "LKOH", "VTBR", "ROSN"] * 20  # Итого 100 запросов

        print(f"Запуск {len(tickers)} запросов с лимитом 0.1 сек...")
        start_time = time.perf_counter()

        # Запускаем всё одновременно
        tasks = [client.share(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.perf_counter()

        # Считаем
        success = [r for r in results if not isinstance(r, Exception)]
        errors = [r for r in results if isinstance(r, Exception)]

        print("\n--- Результаты ---")
        print(f"Успешно: {len(success)}")
        print(f"Ошибок: {len(errors)}")
        print(f"Общее время: {end_time - start_time:.2f} сек")

        if success:
            print(f"Пример данных: {success[0].sec_id} - {success[0].prev_price} руб.")  # type: ignore


if __name__ == "__main__":
    asyncio.run(run_benchmark())
