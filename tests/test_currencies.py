from decimal import Decimal

import pytest
from httpx import Response

from pymoex.exceptions import InstrumentNotFoundError
from tests.conftest import EMPTY_SECURITIES_RESPONSE, MOEX_CURRENCY_JSON


@pytest.mark.asyncio
async def test_currency_found_on_first_market(client, mock_moex) -> None:
    """
    Проверка: валюта найдена сразу на основном рынке selt.
    """
    route = mock_moex.get(
        "/engines/currency/markets/selt/securities/CNYRUB_TOM.json"
    ).mock(return_value=Response(200, json=MOEX_CURRENCY_JSON))

    currency = await client.currency("CNYRUB_TOM")

    assert currency.sec_id == "CNYRUB_TOM"
    assert currency.board_id == "CETS"
    assert currency.short_name == "CNY/RUB TOM"
    assert currency.name == "Китайский юань к российскому рублю"
    assert currency.last_price == Decimal("12.3456")
    assert currency.lot_size == 1000

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_currency_fallback_to_next_market(client, mock_moex) -> None:
    """
    Проверка: если на selt пусто, сервис пробует следующий рынок otcindices.
    """
    selt_route = mock_moex.get(
        "/engines/currency/markets/selt/securities/USDRUBTOMOTC.json"
    ).mock(return_value=Response(200, json=EMPTY_SECURITIES_RESPONSE))

    otc_response = {
        "securities": {
            "columns": [
                "BOARDID",
                "SECID",
                "SHORTNAME",
                "SECNAME",
            ],
            "data": [
                [
                    "OTC",
                    "USDRUBTOMOTC",
                    "USD/RUB OTC",
                    "Внебиржевой доллар США к российскому рублю",
                ],
            ],
        },
        "marketdata": {
            "columns": [
                "BOARDID",
                "SECID",
                "LAST",
            ],
            "data": [
                [
                    "OTC",
                    "USDRUBTOMOTC",
                    92.5,
                ],
            ],
        },
    }

    otc_route = mock_moex.get(
        "/engines/currency/markets/otcindices/securities/USDRUBTOMOTC.json"
    ).mock(return_value=Response(200, json=otc_response))

    currency = await client.currency("USDRUBTOMOTC")

    assert currency.sec_id == "USDRUBTOMOTC"
    assert currency.board_id == "OTC"
    assert currency.short_name == "USD/RUB OTC"
    assert currency.last_price == Decimal("92.5")

    assert selt_route.call_count == 1
    assert otc_route.call_count == 1


@pytest.mark.asyncio
async def test_currency_fallback_skips_failed_market(client, mock_moex) -> None:
    """
    Проверка: если первый рынок вернул HTTP-ошибку,
    сервис пробует следующий рынок.

    Retries отключаем, потому что здесь тестируем fallback рынков,
    а не retry-механику MoexSession.
    """
    client.session.settings.retry_attempts = 1
    client.session.settings.retry_min_wait = 0
    client.session.settings.retry_max_wait = 0
    client.session.settings.request_delay = 0
    client.session.settings.request_jitter = 0

    selt_route = mock_moex.get(
        "/engines/currency/markets/selt/securities/USDRUBTOMOTC.json"
    ).mock(return_value=Response(500, json={"error": "server error"}))

    otc_response = {
        "securities": {
            "columns": [
                "BOARDID",
                "SECID",
                "SHORTNAME",
                "SECNAME",
            ],
            "data": [
                [
                    "OTC",
                    "USDRUBTOMOTC",
                    "USD/RUB OTC",
                    "Внебиржевой доллар США к российскому рублю",
                ],
            ],
        },
        "marketdata": {
            "columns": [
                "BOARDID",
                "SECID",
                "LAST",
            ],
            "data": [
                [
                    "OTC",
                    "USDRUBTOMOTC",
                    92.5,
                ],
            ],
        },
    }

    otc_route = mock_moex.get(
        "/engines/currency/markets/otcindices/securities/USDRUBTOMOTC.json"
    ).mock(return_value=Response(200, json=otc_response))

    currency = await client.currency("USDRUBTOMOTC")

    assert currency.sec_id == "USDRUBTOMOTC"
    assert currency.last_price == Decimal("92.5")

    assert selt_route.call_count == 1
    assert otc_route.call_count == 1


@pytest.mark.asyncio
async def test_currency_not_found_anywhere(client, mock_moex) -> None:
    """
    Проверка: если валюта не найдена ни на одном рынке, выбрасывается InstrumentNotFoundError.
    """
    selt_route = mock_moex.get(
        "/engines/currency/markets/selt/securities/GHOST_TOM.json"
    ).mock(return_value=Response(200, json=EMPTY_SECURITIES_RESPONSE))

    otc_route = mock_moex.get(
        "/engines/currency/markets/otcindices/securities/GHOST_TOM.json"
    ).mock(return_value=Response(200, json=EMPTY_SECURITIES_RESPONSE))

    index_route = mock_moex.get(
        "/engines/currency/markets/index/securities/GHOST_TOM.json"
    ).mock(return_value=Response(200, json=EMPTY_SECURITIES_RESPONSE))

    with pytest.raises(InstrumentNotFoundError, match="Currency GHOST_TOM not found"):
        await client.currency("GHOST_TOM")

    assert selt_route.call_count == 1
    assert otc_route.call_count == 1
    assert index_route.call_count == 1


@pytest.mark.asyncio
async def test_currency_fallback_price_from_close_price(client, mock_moex) -> None:
    """
    Проверка: если LAST отсутствует, модель Currency берёт CLOSEPRICE/WAPRICE/PREVPRICE.
    """
    response = {
        "securities": {
            "columns": [
                "BOARDID",
                "SECID",
                "SHORTNAME",
                "SECNAME",
            ],
            "data": [
                [
                    "CETS",
                    "CNYRUB_TOM",
                    "CNY/RUB TOM",
                    "Китайский юань к российскому рублю",
                ],
            ],
        },
        "marketdata": {
            "columns": [
                "BOARDID",
                "SECID",
                "LAST",
                "CLOSEPRICE",
                "WAPRICE",
                "PREVPRICE",
            ],
            "data": [
                [
                    "CETS",
                    "CNYRUB_TOM",
                    None,
                    12.31,
                    12.22,
                    12.11,
                ],
            ],
        },
    }

    mock_moex.get("/engines/currency/markets/selt/securities/CNYRUB_TOM.json").mock(
        return_value=Response(200, json=response)
    )

    currency = await client.currency("CNYRUB_TOM")

    assert currency.last_price == Decimal("12.31")
    assert currency.close_price == Decimal("12.31")
    assert currency.prev_price == Decimal("12.11")


@pytest.mark.asyncio
async def test_currency_uses_uppercase_secid(client, mock_moex) -> None:
    """
    Проверка: сервис нормализует secid перед запросом.
    """
    route = mock_moex.get(
        "/engines/currency/markets/selt/securities/CNYRUB_TOM.json"
    ).mock(return_value=Response(200, json=MOEX_CURRENCY_JSON))

    currency = await client.currency("cnyrub_tom")

    assert currency.sec_id == "CNYRUB_TOM"
    assert route.call_count == 1
