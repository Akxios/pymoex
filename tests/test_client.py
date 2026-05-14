from unittest.mock import AsyncMock

import pytest

from pymoex.client import MoexClient
from pymoex.core.cache import MemoryCache, NullCache
from pymoex.models.enums import InstrumentType


@pytest.mark.asyncio
async def test_client_default_cache() -> None:
    """
    По умолчанию клиент должен использовать MemoryCache.
    """
    client = MoexClient()

    try:
        assert isinstance(client._cache, MemoryCache)
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_client_disabled_cache() -> None:
    """
    Если use_cache=False, клиент должен использовать NullCache.
    """
    client = MoexClient(use_cache=False)

    try:
        assert isinstance(client._cache, NullCache)
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_client_custom_cache() -> None:
    """
    Клиент должен принимать пользовательский кэш.
    """
    custom_cache = MemoryCache(ttl=999)
    client = MoexClient(cache=custom_cache)

    try:
        assert client._cache is custom_cache
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_client_context_manager_calls_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    async with MoexClient() должен вызвать close() при выходе из блока.
    """
    close_mock = AsyncMock()

    monkeypatch.setattr(MoexClient, "close", close_mock)

    async with MoexClient() as client:
        assert isinstance(client, MoexClient)

    close_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_client_close_clears_cache_and_closes_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    close() должен:
    - очистить кэш;
    - закрыть HTTP-сессию.
    """
    client = MoexClient()

    cache_clear_mock = AsyncMock()
    session_close_mock = AsyncMock()

    monkeypatch.setattr(client._cache, "clear", cache_clear_mock)
    monkeypatch.setattr(client.session, "close", session_close_mock)

    await client.close()

    cache_clear_mock.assert_awaited_once()
    session_close_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_client_proxies_search_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = MoexClient(use_cache=False)
    search_find_mock = AsyncMock(return_value=[])

    monkeypatch.setattr(client.search, "find", search_find_mock)

    try:
        await client.find("SBER")
        await client.find_shares("SBER")
        await client.find_bonds("OFZ")
        await client.find_funds("SBMX")
        await client.find_currencies("CNY")
    finally:
        await client.close()

    assert search_find_mock.call_args_list[0].args == ("SBER", None)
    assert search_find_mock.call_args_list[1].args == ("SBER", InstrumentType.SHARE)
    assert search_find_mock.call_args_list[2].args == ("OFZ", InstrumentType.BOND)
    assert search_find_mock.call_args_list[3].args == ("SBMX", InstrumentType.FUND)
    assert search_find_mock.call_args_list[4].args == ("CNY", InstrumentType.CURRENCY)


@pytest.mark.asyncio
async def test_client_proxies_instrument_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Методы share/bond/fund/currency должны вызывать соответствующие сервисы.

    fund() сейчас использует SharesService.get_share(),
    потому что фонды идут через похожий endpoint/модель.
    """
    client = MoexClient(use_cache=False)

    get_share_mock = AsyncMock(return_value="share-result")
    get_bond_mock = AsyncMock(return_value="bond-result")
    get_currency_mock = AsyncMock(return_value="currency-result")

    monkeypatch.setattr(client.shares, "get_share", get_share_mock)
    monkeypatch.setattr(client.bonds, "get_bond", get_bond_mock)
    monkeypatch.setattr(client.currencies, "get_currency", get_currency_mock)

    try:
        share_result = await client.share("SBER")
        bond_result = await client.bond("SU26238RMFS4")
        fund_result = await client.fund("SBMX")
        currency_result = await client.currency("CNYRUB_TOM")
    finally:
        await client.close()

    assert share_result == "share-result"
    assert bond_result == "bond-result"
    assert fund_result == "share-result"
    assert currency_result == "currency-result"

    assert get_share_mock.call_args_list[0].args == ("SBER",)
    assert get_bond_mock.call_args_list[0].args == ("SU26238RMFS4",)
    assert get_share_mock.call_args_list[1].args == ("SBMX",)
    assert get_currency_mock.call_args_list[0].args == ("CNYRUB_TOM",)


@pytest.mark.asyncio
async def test_client_proxies_event_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Методы dividends/coupons/amortizations должны вызывать сервисы акций/облигаций.
    """
    client = MoexClient(use_cache=False)

    get_dividends_mock = AsyncMock(return_value=[])
    get_coupons_mock = AsyncMock(return_value=[])
    get_amortizations_mock = AsyncMock(return_value=[])

    monkeypatch.setattr(client.shares, "get_dividends", get_dividends_mock)
    monkeypatch.setattr(client.bonds, "get_coupons", get_coupons_mock)
    monkeypatch.setattr(client.bonds, "get_amortizations", get_amortizations_mock)

    try:
        await client.dividends("SBER")
        await client.coupons("SU26238RMFS4")
        await client.amortizations("SU26238RMFS4")
    finally:
        await client.close()

    assert get_dividends_mock.call_args_list[0].args == ("SBER",)
    assert get_coupons_mock.call_args_list[0].args == ("SU26238RMFS4",)
    assert get_amortizations_mock.call_args_list[0].args == ("SU26238RMFS4",)
