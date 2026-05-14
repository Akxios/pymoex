import pytest
import respx
from httpx import Response

import pymoex.api as sync_api
from pymoex import get_share
from pymoex.models.share import Share
from tests.conftest import MOEX_SHARE_JSON


def teardown_sync_manager() -> None:
    """
    Закрывает глобальный sync manager после теста.

    Это важно, потому что sync API держит фоновый event loop
    и общий MoexClient между вызовами.
    """
    if sync_api._manager is not None:
        sync_api._manager.shutdown()
        sync_api._manager = None


def test_sync_get_share() -> None:
    """
    Проверка: синхронная функция get_share() возвращает Share.
    """
    try:
        with respx.mock(base_url="https://iss.moex.com/iss") as mock:
            route = mock.get("/engines/stock/markets/shares/securities/SBER.json").mock(
                return_value=Response(200, json=MOEX_SHARE_JSON)
            )

            share = get_share("SBER")

            assert isinstance(share, Share)
            assert share.sec_id == "SBER"
            assert share.short_name == "Сбербанк"
            assert route.call_count == 1
    finally:
        teardown_sync_manager()


def test_sync_get_share_reuses_global_manager() -> None:
    """
    Проверка: sync API переиспользует один глобальный manager.

    Заодно проверяем кэш: два одинаковых вызова должны дать один HTTP-запрос.
    """
    try:
        with respx.mock(base_url="https://iss.moex.com/iss") as mock:
            route = mock.get("/engines/stock/markets/shares/securities/SBER.json").mock(
                return_value=Response(200, json=MOEX_SHARE_JSON)
            )

            first = get_share("SBER")
            second = get_share("SBER")

            assert first.sec_id == "SBER"
            assert second.sec_id == "SBER"
            assert route.call_count == 1
    finally:
        teardown_sync_manager()


@pytest.mark.asyncio
async def test_sync_api_rejects_running_event_loop() -> None:
    """
    Проверка: sync API нельзя использовать внутри уже запущенного event loop.

    В async-коде пользователь должен использовать MoexClient напрямую.
    """
    with pytest.raises(RuntimeError, match="Cannot use sync API"):
        get_share("SBER")
