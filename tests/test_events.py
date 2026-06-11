from datetime import date
from decimal import Decimal

import pytest
from httpx import Response

from pymoex.client import MoexClient
from tests.conftest import MOEX_BONDIZATION_JSON, MOEX_DIVIDENDS_JSON, MockRouter


@pytest.mark.asyncio
async def test_get_dividends_success(client: MoexClient, mock_moex: MockRouter) -> None:
    """
    Проверка: успешный парсинг списка дивидендов.
    """
    route = mock_moex.get("/securities/SBER/dividends.json").mock(
        return_value=Response(200, json=MOEX_DIVIDENDS_JSON)
    )

    dividends = await client.dividends("SBER")

    assert len(dividends) == 1

    dividend = dividends[0]

    assert dividend.sec_id == "SBER"
    assert dividend.registry_close_date == date(2025, 7, 18)
    assert dividend.value == Decimal("34.84")
    assert dividend.currency_id == "RUB"

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_dividends_empty(client: MoexClient, mock_moex: MockRouter) -> None:
    """
    Проверка: если дивидендов нет, возвращается пустой список.
    """
    route = mock_moex.get("/securities/YNDX/dividends.json").mock(
        return_value=Response(
            200,
            json={
                "dividends": {
                    "columns": [],
                    "data": [],
                },
            },
        )
    )

    dividends = await client.dividends("YNDX")

    assert dividends == []
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_coupons_success(client: MoexClient, mock_moex: MockRouter) -> None:
    """
    Проверка: успешный парсинг купонов по облигации.
    """
    route = mock_moex.get("/securities/SU26238RMFS4/bondization.json").mock(
        return_value=Response(200, json=MOEX_BONDIZATION_JSON)
    )

    coupons = await client.coupons("SU26238RMFS4")

    assert len(coupons) == 1

    coupon = coupons[0]

    assert coupon.sec_id == "SU26238RMFS4"
    assert coupon.isin == "RU000A1038V6"
    assert coupon.coupon_date == date(2026, 6, 10)
    assert coupon.record_date == date(2026, 6, 9)
    assert coupon.value == Decimal("35.4")
    assert coupon.value_prc == Decimal("7.1")
    assert coupon.face_unit == "RUB"

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_coupons_empty(client: MoexClient, mock_moex: MockRouter) -> None:
    """
    Проверка: если купонов нет, возвращается пустой список.
    """
    route = mock_moex.get("/securities/SU26238RMFS4/bondization.json").mock(
        return_value=Response(
            200,
            json={
                "coupons": {
                    "columns": [],
                    "data": [],
                },
            },
        )
    )

    coupons = await client.coupons("SU26238RMFS4")

    assert coupons == []
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_amortizations_success(
    client: MoexClient, mock_moex: MockRouter
) -> None:
    """
    Проверка: успешный парсинг амортизаций по облигации.
    """
    route = mock_moex.get("/securities/SU26238RMFS4/bondization.json").mock(
        return_value=Response(200, json=MOEX_BONDIZATION_JSON)
    )

    amortizations = await client.amortizations("SU26238RMFS4")

    assert len(amortizations) == 1

    amortization = amortizations[0]

    assert amortization.sec_id == "SU26238RMFS4"
    assert amortization.isin == "RU000A1038V6"
    assert amortization.amort_date == date(2041, 5, 15)
    assert amortization.value == Decimal("1000")
    assert amortization.value_prc == Decimal("100")
    assert amortization.face_unit == "RUB"

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_amortizations_empty(
    client: MoexClient, mock_moex: MockRouter
) -> None:
    """
    Проверка: если амортизаций нет, возвращается пустой список.
    """
    route = mock_moex.get("/securities/SU26238RMFS4/bondization.json").mock(
        return_value=Response(
            200,
            json={
                "amortizations": {
                    "columns": [],
                    "data": [],
                },
            },
        )
    )

    amortizations = await client.amortizations("SU26238RMFS4")

    assert amortizations == []
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_get_amortizations_missing_table(
    client: MoexClient, mock_moex: MockRouter
) -> None:
    """
    Проверка: если таблицы amortizations нет в ответе, возвращается пустой список.
    """
    route = mock_moex.get("/securities/SU26238RMFS4/bondization.json").mock(
        return_value=Response(200, json={})
    )

    amortizations = await client.amortizations("SU26238RMFS4")

    assert amortizations == []
    assert route.call_count == 1
