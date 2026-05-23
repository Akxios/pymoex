import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from typing import Self, TypedDict, Unpack

from pymoex.client import MoexClient
from pymoex.core.interfaces import ICache
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.models.currency import Currency
from pymoex.models.dividend import Dividend
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search
from pymoex.models.share import Share


class MoexClientKwargs(TypedDict, total=False):
    cache: ICache | None
    use_cache: bool


def _ensure_no_running_loop() -> None:
    try:
        _ = asyncio.get_running_loop()
    except RuntimeError:
        return

    message = (
        "Cannot use sync API when an event loop is running. "
        "Use MoexClient async API instead."
    )

    raise RuntimeError(message)


def _run_once[T](func: Callable[[MoexClient], Awaitable[T]]) -> T:
    """
    Выполнить один синхронный вызов через временный MoexClient.
    """
    _ensure_no_running_loop()

    async def _main() -> T:
        async with MoexClient() as client:
            return await func(client)

    return asyncio.run(_main())


class SyncMoexClient:
    """
    Синхронная обертка над асинхронным MoexClient.
    """

    _runner: asyncio.Runner
    _client: MoexClient
    _closed: bool

    def __init__(self, **client_kwargs: Unpack[MoexClientKwargs]) -> None:
        _ensure_no_running_loop()

        self._runner = asyncio.Runner()
        self._client = MoexClient(**client_kwargs)
        self._closed = False

    def _run[T](self, coro: Coroutine[object, object, T]) -> T:
        if self._closed:
            raise RuntimeError("SyncMoexClient is already closed.")

        return self._runner.run(coro)

    def close(self) -> None:
        """Явно закрыть ресурсы клиента."""

        if self._closed:
            return

        self._runner.run(self._client.close())
        self._runner.close()
        self._closed = True

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        self.close()

    def share(self, ticker: str) -> Share:
        return self._run(self._client.share(ticker))

    def bond(self, ticker: str) -> Bond:
        return self._run(self._client.bond(ticker))

    def fund(self, ticker: str) -> Share:
        return self._run(self._client.fund(ticker))

    def currency(self, ticker: str) -> Currency:
        return self._run(self._client.currency(ticker))

    def find(
        self,
        query: str,
        instrument_type: InstrumentType | str | None = None,
    ) -> list[Search]:
        return self._run(self._client.find(query, instrument_type))

    def find_shares(self, query: str) -> list[Search]:
        return self._run(self._client.find_shares(query))

    def find_bonds(self, query: str) -> list[Search]:
        return self._run(self._client.find_bonds(query))

    def find_funds(self, query: str) -> list[Search]:
        return self._run(self._client.find_funds(query))

    def find_currencies(self, query: str) -> list[Search]:
        return self._run(self._client.find_currencies(query))

    def dividends(self, ticker: str) -> list[Dividend]:
        return self._run(self._client.dividends(ticker))

    def coupons(self, ticker: str) -> list[Coupon]:
        return self._run(self._client.coupons(ticker))

    def amortizations(self, ticker: str) -> list[Amortization]:
        return self._run(self._client.amortizations(ticker))


def get_share(ticker: str) -> Share:
    """Синхронно получить данные по акции."""
    return _run_once(lambda client: client.share(ticker))


def get_bond(ticker: str) -> Bond:
    """Синхронно получить данные по облигации."""
    return _run_once(lambda client: client.bond(ticker))


def get_fund(ticker: str) -> Share:
    """Синхронно получить данные по фонду."""
    return _run_once(lambda client: client.fund(ticker))


def get_currency(ticker: str) -> Currency:
    """Синхронно получить данные по валюте."""
    return _run_once(lambda client: client.currency(ticker))


def find(
    query: str,
    instrument_type: InstrumentType | str | None = None,
) -> list[Search]:
    """Синхронный поиск по строке."""
    return _run_once(lambda client: client.find(query, instrument_type))


def find_shares(query: str) -> list[Search]:
    """Синхронный поиск акций по строке."""
    return _run_once(lambda client: client.find_shares(query))


def find_bonds(query: str) -> list[Search]:
    """Синхронный поиск облигаций по строке."""
    return _run_once(lambda client: client.find_bonds(query))


def find_funds(query: str) -> list[Search]:
    """Синхронный поиск фондов по строке."""
    return _run_once(lambda client: client.find_funds(query))


def find_currencies(query: str) -> list[Search]:
    """Синхронный поиск валют по строке."""
    return _run_once(lambda client: client.find_currencies(query))


def get_dividends(ticker: str) -> list[Dividend]:
    """Синхронно получить историю дивидендов и будущие выплаты по акции."""
    return _run_once(lambda client: client.dividends(ticker))


def get_coupons(ticker: str) -> list[Coupon]:
    """Синхронно получить историю и график купонов по облигации."""
    return _run_once(lambda client: client.coupons(ticker))


def get_amortizations(ticker: str) -> list[Amortization]:
    """Синхронно получить график амортизации по облигации."""
    return _run_once(lambda client: client.amortizations(ticker))
