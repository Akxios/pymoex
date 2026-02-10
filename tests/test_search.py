import pytest
from httpx import Response

from tests.conftest import MOEX_SEARCH_JSON


@pytest.mark.asyncio
async def test_find_shares(client, mock_moex):
    # Используем JSON из conftest.py
    mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    # Ищем "SBER"
    results = await client.find("SBER")

    assert len(results) > 0
    item = results[0]

    assert item.sec_id == "SBER"
    assert item.short_name == "Сбербанк"
    assert item.is_traded is True


@pytest.mark.asyncio
async def test_find_empty(client, mock_moex):
    # Пустой ответ
    mock_moex.get("/securities.json").mock(
        return_value=Response(200, json={"securities": {"data": [], "columns": []}})
    )

    results = await client.find("NON_EXISTENT")
    assert results == []
