import pytest
from httpx import Response

from pymoex.exceptions import InstrumentNotFoundError
from tests.conftest import MOEX_SHARE_JSON


@pytest.mark.asyncio
async def test_get_share_success(client, mock_moex):
    # Настраиваем мок: при запросе SBER вернуть наш JSON
    mock_moex.get("/engines/stock/markets/shares/securities/SBER.json").mock(
        return_value=Response(200, json=MOEX_SHARE_JSON)
    )

    # Вызываем реальный метод клиента
    share = await client.share("SBER")

    # Проверяем результаты
    assert share.sec_id == "SBER"
    assert share.short_name == "Сбербанк"
    assert share.last_price == 275.5  # Данные из marketdata
    assert share.lot_size == 10  # Данные из securities


@pytest.mark.asyncio
async def test_get_share_not_found(client, mock_moex):
    # Эмулируем пустой ответ (акция не найдена)
    empty_response = {"securities": {"columns": [], "data": []}}

    mock_moex.get("/engines/stock/markets/shares/securities/UNKNOWN.json").mock(
        return_value=Response(200, json=empty_response)
    )

    with pytest.raises(InstrumentNotFoundError):
        await client.share("UNKNOWN")
