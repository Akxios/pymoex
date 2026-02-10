import asyncio

import pytest
from httpx import Response
from tests.conftest import MOEX_SEARCH_JSON


@pytest.mark.asyncio
async def test_search_caching(client, mock_moex):
    # Настраиваем мок
    route = mock_moex.get("/securities.json").mock(
        return_value=Response(200, json=MOEX_SEARCH_JSON)
    )

    # Делаем два запроса подряд
    await client.find("SBER")
    await client.find("SBER")

    # Проверяем, что реальный HTTP запрос ушел ТОЛЬКО ОДИН
    assert route.call_count == 1


@pytest.mark.asyncio
async def test_request_coalescing(client, mock_moex):
    """
    Проверяем, что если 2 запроса приходят одновременно,
    выполняется только один HTTP-запрос.
    """
    route = mock_moex.get("/securities.json").mock(
        side_effect=lambda request: Response(200, json=MOEX_SEARCH_JSON)
    )

    # Запускаем 5 одновременных запросов
    tasks = [client.find("SBER") for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # Все должны получить результат
    assert len(results) == 5
    assert results[0][0].sec_id == "SBER"

    # Но HTTP запрос должен быть ровно 1
    assert route.call_count == 1
