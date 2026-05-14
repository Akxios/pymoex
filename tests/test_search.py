import pytest
from httpx import Response

from pymoex.models.enums import InstrumentType
from tests.conftest import MOEX_SEARCH_JSON


@pytest.mark.asyncio
async def test_find_all_returns_ranked_results(client, mock_moex) -> None:
    """
    Проверка: общий поиск возвращает подходящие результаты.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    results = await client.find("SBER")

    assert len(results) == 2

    assert results[0].sec_id == "SBER"
    assert results[0].short_name == "Сбербанк"
    assert results[0].is_traded is True

    assert results[1].sec_id == "SBERP"

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_empty_response_returns_empty_list(client, mock_moex) -> None:
    """
    Проверка: если MOEX вернул пустую таблицу, возвращается пустой список.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(
            200,
            json={
                "securities": {
                    "columns": [],
                    "data": [],
                },
            },
        )
    )

    results = await client.find("NON_EXISTENT")

    assert results == []
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_empty_query_does_not_call_api(client, mock_moex) -> None:
    """
    Проверка: пустой query сразу возвращает [],
    без HTTP-запроса.
    """
    results = await client.find("   ")

    assert results == []
    assert len(mock_moex.calls) == 0


@pytest.mark.asyncio
async def test_find_shares_filters_by_share_type(client, mock_moex) -> None:
    """
    Проверка: find_shares() оставляет только акции.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    results = await client.find_shares("SBER")

    assert [item.sec_id for item in results] == ["SBER", "SBERP"]
    assert all(item.group == "stock_shares" for item in results)

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_bonds_filters_by_bond_type(client, mock_moex) -> None:
    """
    Проверка: find_bonds() оставляет только облигации.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    results = await client.find_bonds("ОФЗ")

    assert len(results) == 1
    assert results[0].sec_id == "SU26238RMFS4"
    assert results[0].group == "stock_bonds"

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_funds_filters_by_fund_type(client, mock_moex) -> None:
    """
    Проверка: find_funds() оставляет только фонды.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    results = await client.find_funds("SBMX")

    assert len(results) == 1
    assert results[0].sec_id == "SBMX"
    assert results[0].group == "stock_ppif"

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_currencies_filters_by_currency_type(client, mock_moex) -> None:
    """
    Проверка: find_currencies() оставляет только валютные инструменты.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    results = await client.find_currencies("CNY")

    assert len(results) == 1
    assert results[0].sec_id == "CNYRUB_TOM"
    assert results[0].group == "currency_selt"

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_accepts_instrument_type_string(client, mock_moex) -> None:
    """
    Проверка: client.find(..., instrument_type='share')
    работает так же, как InstrumentType.SHARE.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    results = await client.find("SBER", instrument_type="share")

    assert [item.sec_id for item in results] == ["SBER", "SBERP"]
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_accepts_instrument_type_enum(client, mock_moex) -> None:
    """
    Проверка: client.find(..., instrument_type=InstrumentType.BOND)
    фильтрует по enum.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    results = await client.find("ОФЗ", instrument_type=InstrumentType.BOND)

    assert len(results) == 1
    assert results[0].sec_id == "SU26238RMFS4"
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_rejects_unknown_instrument_type(client) -> None:
    """
    Проверка: неизвестный тип инструмента даёт ValueError.
    """
    with pytest.raises(ValueError, match="Unknown instrument type"):
        await client.find("SBER", instrument_type="unknown")


@pytest.mark.asyncio
async def test_find_deduplicates_by_secid(client, mock_moex) -> None:
    """
    Проверка: если MOEX вернул один SECID несколько раз,
    результат содержит только первый вариант.
    """
    response = {
        "securities": {
            "columns": [
                "secid",
                "shortname",
                "name",
                "group",
                "is_traded",
            ],
            "data": [
                [
                    "SBER",
                    "Сбербанк",
                    "ПАО Сбербанк",
                    "stock_shares",
                    1,
                ],
                [
                    "sber",
                    "Сбербанк duplicate",
                    "ПАО Сбербанк duplicate",
                    "stock_shares",
                    1,
                ],
            ],
        },
    }

    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=response)
    )

    results = await client.find("SBER")

    assert len(results) == 1
    assert results[0].sec_id == "SBER"
    assert results[0].short_name == "Сбербанк"

    assert route.call_count == 1


@pytest.mark.asyncio
async def test_find_sends_normalized_query_params(client, mock_moex) -> None:
    """
    Проверка: query нормализуется перед отправкой в MOEX.

    '  SBER  ' должен уйти как q=sber.
    """
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    await client.find("  SBER  ")

    request = route.calls.last.request

    assert "q=sber" in str(request.url)
    assert "limit=1000" in str(request.url)
