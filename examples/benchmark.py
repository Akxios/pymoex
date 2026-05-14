import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from pymoex import MoexClient
from pymoex.models.share import Share

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    total: int
    success: int
    errors: int
    elapsed: float


async def run_case(
    name: str,
    factory: Callable[[], Awaitable[list[Share | Exception]]],
) -> BenchmarkResult:
    """
    Запускает один benchmark-сценарий и печатает результат.
    """
    print(f"\n--- {name} ---")

    start = time.perf_counter()
    results = await factory()
    elapsed = time.perf_counter() - start

    success = [item for item in results if not isinstance(item, Exception)]
    errors = [item for item in results if isinstance(item, Exception)]

    print(f"Всего вызовов: {len(results)}")
    print(f"Успешно: {len(success)}")
    print(f"Ошибок: {len(errors)}")
    print(f"Время: {elapsed:.2f} сек")

    if success:
        example = success[0]
        print(
            "Пример: "
            f"{example.sec_id} | "
            f"{example.short_name} | "
            f"last={example.last_price}"
        )

    if errors:
        print(f"Первая ошибка: {errors[0]!r}")

    return BenchmarkResult(
        name=name,
        total=len(results),
        success=len(success),
        errors=len(errors),
        elapsed=elapsed,
    )


async def fetch_many_shares(
    client: MoexClient,
    tickers: list[str],
) -> list[Share | Exception]:
    """
    Параллельно запрашивает список акций.
    """
    tasks = [client.share(ticker) for ticker in tickers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return list(results)


async def benchmark_with_cache() -> BenchmarkResult:
    """
    Benchmark с включённым кэшем.

    Здесь тикеры повторяются много раз, поэтому MemoryCache должен
    сильно сократить число реальных HTTP-запросов.
    """
    tickers = ["SBER", "GAZP", "LKOH", "VTBR", "ROSN"] * 20

    async with MoexClient(use_cache=True) as client:
        client.session.settings.request_delay = 0.1
        client.session.settings.request_jitter = 0

        return await run_case(
            name="С кэшем: 100 вызовов по 5 повторяющимся тикерам",
            factory=lambda: fetch_many_shares(client, tickers),
        )


async def benchmark_without_cache() -> BenchmarkResult:
    """
    Benchmark с выключенным кэшем.

    Здесь каждый вызов идёт в HTTP-слой, поэтому этот сценарий лучше
    показывает работу rate limit.
    """
    tickers = ["SBER", "GAZP", "LKOH", "VTBR", "ROSN"] * 5

    async with MoexClient(use_cache=False) as client:
        client.session.settings.request_delay = 0.1
        client.session.settings.request_jitter = 0

        return await run_case(
            name="Без кэша: 25 реальных запросов",
            factory=lambda: fetch_many_shares(client, tickers),
        )


async def main() -> None:
    """
    Запускает benchmark для async API.
    """
    print("pymoex benchmark")
    print("Rate limit: request_delay=0.1, request_jitter=0")

    cached = await benchmark_with_cache()
    uncached = await benchmark_without_cache()

    print("\n--- Сравнение ---")
    print(f"С кэшем:    {cached.elapsed:.2f} сек")
    print(f"Без кэша:   {uncached.elapsed:.2f} сек")

    if cached.elapsed > 0:
        ratio = uncached.elapsed / cached.elapsed
        print(f"Разница:    примерно x{ratio:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
