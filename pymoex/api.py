import asyncio
import atexit
import threading
from collections.abc import Awaitable, Callable
from concurrent.futures import TimeoutError as FutureTimeoutError
from contextlib import suppress

from pymoex.client import MoexClient
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.models.currency import Currency
from pymoex.models.dividend import Dividend
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search
from pymoex.models.share import Share


async def _await_result[T](awaitable: Awaitable[T]) -> T:
    return await awaitable


def _ensure_no_running_loop() -> None:
    try:
        _ = asyncio.get_running_loop()
    except RuntimeError:
        return

    message = (
        "Cannot use sync API when an event loop is running. "
        "Use MoexClient (async API) instead."
    )
    raise RuntimeError(message)


class _SyncManager:
    """
    Менеджер фонового цикла событий для синхронного API.
    Обеспечивает жизнь единого MoexClient между вызовами.
    """

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._thread: threading.Thread = threading.Thread(
            target=self._run_loop,
            name="PymoexSyncThread",
            daemon=True,
        )
        self._closed: bool = False

        self._thread.start()

        future = asyncio.run_coroutine_threadsafe(self._init_client(), self._loop)
        self.client: MoexClient = future.result()

        _ = atexit.register(self.shutdown)

    @property
    def is_closed(self) -> bool:
        """Свойство для безопасной проверки статуса менеджера."""
        return self._closed

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _init_client(self) -> MoexClient:
        return MoexClient()

    async def _close_client(self) -> None:
        await self.client.close()

    def shutdown(self) -> None:
        """Остановка цикла и закрытие HTTP-сессии."""

        if self._closed:
            return

        self._closed = True

        if self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._close_client(), self._loop)

            with suppress(FutureTimeoutError, RuntimeError):
                future.result(timeout=2)

            _ = self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread.is_alive():
            self._thread.join(timeout=2)

        if not self._loop.is_closed() and not self._thread.is_alive():
            self._loop.close()

    def execute[T](self, awaitable: Awaitable[T]) -> T:
        """Запуск корутины в фоновом потоке с ожиданием результата."""

        if self._closed:
            raise RuntimeError("Sync manager is already closed.")

        future = asyncio.run_coroutine_threadsafe(
            _await_result(awaitable),
            self._loop,
        )

        return future.result()


_manager: _SyncManager | None = None


def _get_manager() -> _SyncManager:
    global _manager

    if _manager is None or _manager.is_closed:
        _manager = _SyncManager()

    return _manager


def _run_client_call[T](func: Callable[[MoexClient], Awaitable[T]]) -> T:
    """
    Выполняет асинхронный вызов, переиспользуя глобальный клиент
    в фоновом потоке, чтобы сохранить кэш и пул соединений.
    """
    _ensure_no_running_loop()

    manager = _get_manager()
    return manager.execute(func(manager.client))


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


def find(
    query: str, instrument_type: InstrumentType | str | None = None
) -> list[Search]:
    """
    Синхронный поиск по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список Search
    """

    return _run_client_call(lambda c: c.find(query, instrument_type))


def find_shares(query: str) -> list[Search]:
    """
    Синхронный поиск акций по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список Search
    """

    return _run_client_call(lambda c: c.find_shares(query))


def find_bonds(query: str) -> list[Search]:
    """
    Синхронный поиск облигаций по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список Search
    """

    return _run_client_call(lambda c: c.find_bonds(query))


def find_funds(query: str) -> list[Search]:
    """
    Синхронный поиск фондов по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список Search
    """
    return _run_client_call(lambda c: c.find_funds(query))


def find_currencies(query: str) -> list[Search]:
    """
    Синхронный поиск валют по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список Search
    """
    return _run_client_call(lambda c: c.find_currencies(query))


def get_dividends(ticker: str) -> list[Dividend]:
    """
    Синхронно получить историю дивидендов и будущие утвержденные выплаты по акции.

    :param ticker: тикер акции (например, 'SBER')
    :return: список объектов Dividend
    """

    return _run_client_call(lambda c: c.dividends(ticker))


def get_coupons(ticker: str) -> list[Coupon]:
    """
    Синхронно получить историю и график купонов по облигации.

    :param ticker: тикер облигации (например, 'SBERP')
    :return: список объектов Coupon
    """

    return _run_client_call(lambda c: c.coupons(ticker))


def get_amortizations(ticker: str) -> list[Amortization]:
    """
    Синхронно получить график амортизации по облигации.

    :param ticker: тикер облигации (например, 'SBERP')
    :return: список объектов Amortization
    """

    return _run_client_call(lambda c: c.amortizations(ticker))


def get_fund(ticker: str) -> Share:
    """
    Синхронно получить данные по фонду (ПИФ/ETF).

    :param ticker: тикер фонда (например, 'SBER')
    :return: объект Share
    """
    return _run_client_call(lambda c: c.fund(ticker))


def get_currency(ticker: str) -> Currency:
    """
    Синхронно получить данные по валюте.

    :param ticker: тикер валютной пары (например, 'CNYRUB_TOM')
    :return: объект Currency
    """
    return _run_client_call(lambda c: c.currency(ticker))
