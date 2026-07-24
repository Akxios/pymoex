from decimal import Decimal

import pytest
from httpx import Response

from pymoex.client import MoexClient
from pymoex.core.constants import CacheTTL
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from tests.conftest import EMPTY_SECURITIES_RESPONSE, MOEX_BOND_JSON, MockRouter


@pytest.mark.asyncio
async def test_get_bond_success(client: MoexClient, mock_moex: MockRouter) -> None:
    """
    Проверка: успешное получение облигации.

    Сервис должен:
    - запросить bond endpoint;
    - выбрать лучшую board;
    - собрать данные из securities, marketdata и marketdata_yields;
    - вернуть модель Bond.
    """
    _ = mock_moex.get("/engines/stock/markets/bonds/securities/SU26238RMFS4.json").mock(
        return_value=Response(200, json=MOEX_BOND_JSON)
    )

    bond = await client.bond("SU26238RMFS4")

    assert bond.sec_id == "SU26238RMFS4"
    assert bond.short_name == "ОФЗ 26238"
    assert bond.name == "ОФЗ-ПД 26238"
    assert bond.board_id == "TQOB"

    assert bond.face_value == Decimal("1000")
    assert bond.face_unit == "RUB"

    assert bond.coupon_value == Decimal("35.4")
    assert bond.coupon_percent == Decimal("7.1")

    assert bond.price_percent == Decimal("72.5")
    assert bond.last_yield == Decimal("14.2")
    assert bond.effective_yield == Decimal("14.5")

    assert bond.last_price == Decimal("725")
    assert bond.last_dirty_price == Decimal("737.3")


def test_bonds_service_uses_quote_ttl() -> None:
    client = MoexClient()

    assert client.bonds.ttl == CacheTTL.BOND_TTL_SECONDS


def test_bond_preserves_zero_price_and_yield() -> None:
    bond = Bond.model_validate(
        {
            "SECID": "SU26238RMFS4",
            "SHORTNAME": "ОФЗ 26238",
            "LAST": 0,
            "PREV": 70.1,
            "EFFECTIVEYIELD": 0,
            "YIELD": 14.2,
        }
    )

    assert bond.price_percent == Decimal("0")
    assert bond.effective_yield == Decimal("0")


@pytest.mark.asyncio
async def test_get_bond_not_found(client: MoexClient, mock_moex: MockRouter) -> None:
    """
    Проверка: если таблица securities пустая,
    сервис выбрасывает InstrumentNotFoundError.
    """
    _ = mock_moex.get("/engines/stock/markets/bonds/securities/FAKE_BOND.json").mock(
        return_value=Response(200, json=EMPTY_SECURITIES_RESPONSE)
    )

    with pytest.raises(InstrumentNotFoundError, match="Bond FAKE_BOND not found"):
        _ = await client.bond("FAKE_BOND")


@pytest.mark.asyncio
async def test_get_bond_fallback_price_from_prev_weighted_price(
    client: MoexClient, mock_moex: MockRouter
) -> None:
    """
    Проверка: если LAST отсутствует, модель берёт PREV или PREVWAPRICE.

    В текущей модели Bond fallback устроен так:
    LAST = PREV or PREVWAPRICE
    """
    response: dict[str, object] = {
        "securities": {
            "columns": [
                "BOARDID",
                "SECID",
                "SHORTNAME",
                "SECNAME",
                "FACEVALUE",
            ],
            "data": [
                [
                    "TQOB",
                    "SU26238RMFS4",
                    "ОФЗ 26238",
                    "ОФЗ-ПД 26238",
                    1000,
                ],
            ],
        },
        "marketdata": {
            "columns": [
                "BOARDID",
                "SECID",
                "LAST",
                "PREVWAPRICE",
            ],
            "data": [
                [
                    "TQOB",
                    "SU26238RMFS4",
                    None,
                    64.8,
                ],
            ],
        },
        "marketdata_yields": {
            "columns": [],
            "data": [],
        },
    }

    _ = mock_moex.get("/engines/stock/markets/bonds/securities/SU26238RMFS4.json").mock(
        return_value=Response(200, json=response)
    )

    bond = await client.bond("SU26238RMFS4")

    assert bond.price_percent == Decimal("64.8")
    assert bond.prev_weighted_price == Decimal("64.8")
    assert bond.last_price == Decimal("648")


@pytest.mark.asyncio
async def test_get_bond_prefers_prev_over_prev_weighted_price(
    client: MoexClient, mock_moex: MockRouter
) -> None:
    """
    Проверка: если LAST нет, но есть PREV и PREVWAPRICE, модель выбирает PREV.

    Это соответствует текущему валидатору:
    data["LAST"] = data.get("PREV") or data.get("PREVWAPRICE")
    """
    response: dict[str, object] = {
        "securities": {
            "columns": [
                "BOARDID",
                "SECID",
                "SHORTNAME",
                "SECNAME",
                "FACEVALUE",
            ],
            "data": [
                [
                    "TQOB",
                    "SU26238RMFS4",
                    "ОФЗ 26238",
                    "ОФЗ-ПД 26238",
                    1000,
                ],
            ],
        },
        "marketdata": {
            "columns": [
                "BOARDID",
                "SECID",
                "LAST",
                "PREV",
                "PREVWAPRICE",
            ],
            "data": [
                [
                    "TQOB",
                    "SU26238RMFS4",
                    None,
                    70.1,
                    64.8,
                ],
            ],
        },
        "marketdata_yields": {
            "columns": [],
            "data": [],
        },
    }

    _ = mock_moex.get("/engines/stock/markets/bonds/securities/SU26238RMFS4.json").mock(
        return_value=Response(200, json=response)
    )

    bond = await client.bond("SU26238RMFS4")

    assert bond.price_percent == Decimal("70.1")
    assert bond.prev == Decimal("70.1")
    assert bond.prev_weighted_price == Decimal("64.8")
    assert bond.last_price == Decimal("701")


@pytest.mark.asyncio
async def test_get_bond_uses_uppercase_ticker(
    client: MoexClient, mock_moex: MockRouter
) -> None:
    """
    Проверка: сервис нормализует тикер перед запросом.
    """
    route = mock_moex.get(
        "/engines/stock/markets/bonds/securities/SU26238RMFS4.json"
    ).mock(return_value=Response(200, json=MOEX_BOND_JSON))

    bond = await client.bond("su26238rmfs4")

    assert bond.sec_id == "SU26238RMFS4"
    assert route.call_count == 1
