from decimal import Decimal

import pytest
from httpx import Response

from pymoex.exceptions import InstrumentNotFoundError
from tests.conftest import EMPTY_SECURITIES_RESPONSE, MOEX_SHARE_JSON


@pytest.mark.asyncio
async def test_get_share_success(client, mock_moex) -> None:
    """
    Проверка: успешное получение акции.

    Сервис должен:
    - запросить share endpoint;
    - собрать данные из securities и marketdata;
    - вернуть модель Share.
    """
    route = mock_moex.get("/engines/stock/markets/shares/securities/SBER.json").mock(
        return_value=Response(200, json=MOEX_SHARE_JSON)
    )

    share = await client.share("SBER")

    assert share.sec_id == "SBER"
    assert share.short_name == "Сбербанк"
    assert share.name == "Сбербанк России"
    assert share.board_id == "TQBR"
    assert share.isin == "RU0009029540"

    assert share.last_price == Decimal("275.5")
    assert share.open_price == Decimal("270.0")
    assert share.lot_size == 10

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_share_not_found(client, mock_moex) -> None:
    """
    Проверка: если securities пустой, выбрасывается InstrumentNotFoundError.
    """
    route = mock_moex.get("/engines/stock/markets/shares/securities/UNKNOWN.json").mock(
        return_value=Response(200, json=EMPTY_SECURITIES_RESPONSE)
    )

    with pytest.raises(InstrumentNotFoundError, match="Share UNKNOWN not found"):
        await client.share("UNKNOWN")

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_share_uses_uppercase_ticker(client, mock_moex) -> None:
    """
    Проверка: сервис нормализует тикер перед запросом.
    """
    route = mock_moex.get("/engines/stock/markets/shares/securities/SBER.json").mock(
        return_value=Response(200, json=MOEX_SHARE_JSON)
    )

    share = await client.share("sber")

    assert share.sec_id == "SBER"
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_share_fallback_price_from_close_price(client, mock_moex) -> None:
    """
    Проверка: если LAST отсутствует, Share берёт CLOSEPRICE.
    """
    response = {
        "securities": {
            "columns": [
                "SECID",
                "SHORTNAME",
                "SECNAME",
                "BOARDID",
                "LOTSIZE",
            ],
            "data": [
                [
                    "SBER",
                    "Сбербанк",
                    "Сбербанк России",
                    "TQBR",
                    10,
                ],
            ],
        },
        "marketdata": {
            "columns": [
                "SECID",
                "BOARDID",
                "LAST",
                "CLOSEPRICE",
                "PREVPRICE",
                "PREVWAPRICE",
            ],
            "data": [
                [
                    "SBER",
                    "TQBR",
                    None,
                    281.1,
                    279.0,
                    278.5,
                ],
            ],
        },
        "marketdata_yields": {
            "columns": [],
            "data": [],
        },
    }

    mock_moex.get("/engines/stock/markets/shares/securities/SBER.json").mock(
        return_value=Response(200, json=response)
    )

    share = await client.share("SBER")

    assert share.last_price == Decimal("281.1")
    assert share.close_price == Decimal("281.1")
    assert share.prev_price == Decimal("279.0")
    assert share.prev_weighted_price == Decimal("278.5")


@pytest.mark.asyncio
async def test_get_share_fallback_price_from_prev_price(client, mock_moex) -> None:
    """
    Проверка: если LAST и CLOSEPRICE отсутствуют, Share берёт PREVPRICE.
    """
    response = {
        "securities": {
            "columns": [
                "SECID",
                "SHORTNAME",
                "SECNAME",
                "BOARDID",
            ],
            "data": [
                [
                    "SBER",
                    "Сбербанк",
                    "Сбербанк России",
                    "TQBR",
                ],
            ],
        },
        "marketdata": {
            "columns": [
                "SECID",
                "BOARDID",
                "LAST",
                "CLOSEPRICE",
                "PREVPRICE",
                "PREVWAPRICE",
            ],
            "data": [
                [
                    "SBER",
                    "TQBR",
                    None,
                    None,
                    279.0,
                    278.5,
                ],
            ],
        },
        "marketdata_yields": {
            "columns": [],
            "data": [],
        },
    }

    mock_moex.get("/engines/stock/markets/shares/securities/SBER.json").mock(
        return_value=Response(200, json=response)
    )

    share = await client.share("SBER")

    assert share.last_price == Decimal("279.0")
    assert share.prev_price == Decimal("279.0")
    assert share.prev_weighted_price == Decimal("278.5")


@pytest.mark.asyncio
async def test_get_share_fallback_price_from_prev_weighted_price(
    client,
    mock_moex,
) -> None:
    """
    Проверка: если LAST, CLOSEPRICE и PREVPRICE отсутствуют,
    Share берёт PREVWAPRICE.
    """
    response = {
        "securities": {
            "columns": [
                "SECID",
                "SHORTNAME",
                "SECNAME",
                "BOARDID",
            ],
            "data": [
                [
                    "SBER",
                    "Сбербанк",
                    "Сбербанк России",
                    "TQBR",
                ],
            ],
        },
        "marketdata": {
            "columns": [
                "SECID",
                "BOARDID",
                "LAST",
                "CLOSEPRICE",
                "PREVPRICE",
                "PREVWAPRICE",
            ],
            "data": [
                [
                    "SBER",
                    "TQBR",
                    None,
                    None,
                    None,
                    278.5,
                ],
            ],
        },
        "marketdata_yields": {
            "columns": [],
            "data": [],
        },
    }

    mock_moex.get("/engines/stock/markets/shares/securities/SBER.json").mock(
        return_value=Response(200, json=response)
    )

    share = await client.share("SBER")

    assert share.last_price == Decimal("278.5")
    assert share.prev_weighted_price == Decimal("278.5")
