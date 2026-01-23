import asyncio
from typing import Any
from pymoex.client import MoexClient


def _run_sync(coro):
    """
    Запуск асинхронной корутины в синхронном контексте.

    - Если event loop не запущен, используется asyncio.run()
    - Если loop уже существует (например, Jupyter, FastAPI),
      выбрасывается ошибка и предлагается использовать async API напрямую.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Нет активного event loop — можно безопасно запустить
        return asyncio.run(coro)
    else:
        # Event loop уже запущен (например, в Jupyter)
        raise RuntimeError("Event loop is already running; use async API instead")


def get_share(ticker: str) -> Any:
    """
    Синхронно получить данные по акции.

    :param ticker: тикер акции (например, 'SBER')
    :return: объект Share
    """
    async def _main():
        async with MoexClient() as client:
            return await client.share(ticker)

    return _run_sync(_main())


def get_bond(ticker: str) -> Any:
    """
    Синхронно получить данные по облигации.

    :param ticker: ISIN или торговый код
    :return: объект Bond
    """
    async def _main():
        async with MoexClient() as client:
            return await client.bond(ticker)

    return _run_sync(_main())


def find_shares(query: str):
    """
    Синхронный поиск акций по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список SearchResult
    """
    async def _main():
        async with MoexClient() as client:
            return await client.find_shares(query)

    return _run_sync(_main())


def find_bonds(query: str):
    """
    Синхронный поиск облигаций по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список SearchResult
    """
    async def _main():
        async with MoexClient() as client:
            return await client.find_bonds(query)

    return _run_sync(_main())
