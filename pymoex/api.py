import asyncio
import atexit
import threading
from typing import Any, Callable, Coroutine, List, TypeVar

from pymoex.client import MoexClient
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.models.dividend import Dividend
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search
from pymoex.models.share import Share

T = TypeVar("T")


class _SyncManager:
    """
    Менеджер фонового цикла событий для синхронного API.
    Обеспечивает жизнь единого MoexClient (и его кэша/сессии) между вызовами.
    """

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop, name="PymoexSyncThread", daemon=True
        )
        self._thread.start()

        # Инициализируем клиента внутри фонового цикла
        future = asyncio.run_coroutine_threadsafe(self._init_client(), self._loop)
        self.client = future.result()

        # Регистрируем хук для корректного закрытия сессий при выходе
        atexit.register(self.shutdown)

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _init_client(self) -> MoexClient:
        return MoexClient()

    async def _close_client(self):
        await self.client.close()

    def shutdown(self):
        """Остановка цикла и закрытие HTTP-сессии."""
        if self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._close_client(), self._loop)
            try:
                future.result(timeout=2)
            except Exception:
                pass
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread.is_alive():
            self._thread.join(timeout=2)

    def execute(self, coro: Coroutine[Any, Any, T]) -> T:
        """Запуск корутины в фоновом потоке с ожиданием результата."""

        # Проверяем, не запущен ли уже event loop в текущем потоке (FastAPI, Jupyter)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            raise RuntimeError(
                "Cannot use sync API when an event loop is running. "
                "Use MoexClient (async API) instead."
            )

        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()


# Глобальный экземпляр менеджера
_manager = None


def _get_manager() -> _SyncManager:
    global _manager
    if _manager is None:
        _manager = _SyncManager()
    return _manager


def _run_client_call(func: Callable[[MoexClient], Coroutine[Any, Any, T]]) -> T:
    """
    Выполняет асинхронный вызов, переиспользуя глобальный клиент
    в фоновом потоке, чтобы сохранить кэш и пул соединений.
    """
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


def find_shares(query: str) -> List[Search]:
    """
    Синхронный поиск акций по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список Search
    """

    return _run_client_call(lambda c: c.find_shares(query))


def find_bonds(query: str) -> List[Search]:
    """
    Синхронный поиск облигаций по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список Search
    """

    return _run_client_call(lambda c: c.find_bonds(query))


def find(
    query: str, instrument_type: InstrumentType | str | None = None
) -> List[Search]:
    """
    Синхронный поиск по строке.

    :param query: тикер, название, ISIN, эмитент
    :return: список Search
    """

    return _run_client_call(lambda c: c.find(query, instrument_type))


def get_dividends(ticker: str) -> List[Dividend]:
    """
    Синхронно получить историю дивидендов и будущие утвержденные выплаты по акции.

    :param ticker: тикер акции (например, 'SBER')
    :return: список объектов Dividend
    """

    return _run_client_call(lambda c: c.dividends(ticker))


def get_coupons(ticker: str) -> List[Coupon]:
    """
    Синхронно получить историю и график купонов по облигации.

    :param ticker: тикер облигации (например, 'SBERP')
    :return: список объектов Coupon
    """

    return _run_client_call(lambda c: c.coupons(ticker))


def get_amortizations(ticker: str) -> List[Amortization]:
    """
    Синхронно получить график амортизации по облигации.

    :param ticker: тикер облигации (например, 'SBERP')
    :return: список объектов Amortization
    """

    return _run_client_call(lambda c: c.amortizations(ticker))
