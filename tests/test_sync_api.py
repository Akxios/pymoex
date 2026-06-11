import pytest
import respx
from httpx import Response

from pymoex import get_share
from pymoex.models.share import Share
from tests.conftest import MOEX_SHARE_JSON


def test_sync_get_share() -> None:
    """
    Проверка: синхронная функция get_share() возвращает Share.
    """

    with respx.mock(base_url="https://iss.moex.com/iss") as mock:
        route = mock.get("/engines/stock/markets/shares/securities/SBER.json").mock(
            return_value=Response(200, json=MOEX_SHARE_JSON)
        )

        share = get_share("SBER")

        assert isinstance(share, Share)
        assert share.sec_id == "SBER"
        assert share.short_name == "Сбербанк"
        assert route.call_count == 1


def test_sync_get_share_is_one_shot() -> None:
    with respx.mock(base_url="https://iss.moex.com/iss") as mock:
        route = mock.get("/engines/stock/markets/shares/securities/SBER.json").mock(
            return_value=Response(200, json=MOEX_SHARE_JSON)
        )

        first = get_share("SBER")
        second = get_share("SBER")

        assert first.sec_id == "SBER"
        assert second.sec_id == "SBER"
        assert route.call_count == 2


@pytest.mark.asyncio
async def test_sync_api_rejects_running_event_loop() -> None:
    """
    Проверка: sync API нельзя использовать внутри уже запущенного event loop.
    """
    with pytest.raises(RuntimeError, match="Cannot use sync API"):
        _ = get_share("SBER")
