import asyncio
from typing import Awaitable, Callable, List, TypeVar

from pymoex.client import MoexClient
from pymoex.models.bond import Bond
from pymoex.models.search import SearchResult
from pymoex.models.share import Share

T = TypeVar("T")


def _run_sync(coro):
    """
    Запуск асинхронной корутины в синхронном контексте.

    - Если event loop не запущен, используется asyncio.run()
    - Если loop уже существует (например, Jupyter, FastAPI),
      выбрасывается ошибка и предлагается использовать async API напрямую.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # Нет активного event loop — можно безопасно запустить
        return asyncio.run(coro)
    else:
        # Event loop уже запущен (например, в Jupyter)
        raise RuntimeError(
            "Cannot use sync API when an event loop is running. "
            "Use MoexClient (async API) instead."
        )


def _run_client_call(func: Callable[[MoexClient], Awaitable[T]]) -> T:
    async def _main():
        async with MoexClient() as client:
            return await func(client)

    return _run_sync(_main())


def get_share(ticker: str) -> Share:
    """
    Синхронно получить данные по акции.

    :param ticker: тикер акции (например, 'SBER')
    :return: объект Share
    """

    return _run_client_call(lambda c: c.share(ticker))


def get_bond(ticker: str) -> Bond:
    """
    Синхронно получить данные по облигации.

    :param ticker: ISIN или торговый код
    :return: объект Bond
    """

    return _run_client_call(lambda c: c.bond(ticker))


def find_shares(query: str) -> List[SearchResult]:
    """
    Синхронный поиск акций по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список SearchResult
    """

    return _run_client_call(lambda c: c.find_shares(query))


def find_bonds(query: str) -> List[SearchResult]:
    """
    Синхронный поиск облигаций по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список SearchResult
    """

    return _run_client_call(lambda c: c.find_bonds(query))
