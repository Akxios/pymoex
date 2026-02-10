import pytest
import pytest_asyncio
import respx

from pymoex.client import MoexClient

# Пример ответа MOEX для акции
MOEX_SHARE_JSON = {
    "securities": {
        "columns": ["SECID", "SHORTNAME", "LOTSIZE", "ISIN", "BOARDID"],
        "data": [["SBER", "Сбербанк", 10, "RU0009029540", "TQBR"]],
    },
    "marketdata": {
        "columns": ["SECID", "LAST", "OPEN", "BOARDID"],
        "data": [["SBER", 275.5, 270.0, "TQBR"]],
    },
}

# Пример ответа поиска
MOEX_SEARCH_JSON = {
    "securities": {
        "columns": ["secid", "shortname", "name", "group", "is_traded"],
        "data": [
            ["SBER", "Сбербанк", "ПАО Сбербанк", "stock_shares", 1],
            ["SBERP", "Сбербанк-п", "ПАО Сбербанк прив.", "stock_shares", 1],
        ],
    }
}


@pytest_asyncio.fixture
async def client():
    async with MoexClient() as c:
        yield c


# Для синхронных фикстур можно оставить обычный @pytest.fixture
@pytest.fixture
def mock_moex(client):
    """Мок для перехвата запросов к iss.moex.com"""
    # Используем настройки клиента для получения base_url
    with respx.mock(base_url=client.session.settings.base_url) as respx_mock:
        yield respx_mock
