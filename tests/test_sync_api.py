import respx

from pymoex import get_share
from pymoex.models.share import Share
from tests.conftest import MOEX_SHARE_JSON


def test_sync_get_share():
    # Для синхронного теста мокаем глобально через декоратор или контекст
    with respx.mock(base_url="https://iss.moex.com/iss") as mock:
        mock.get("/engines/stock/markets/shares/securities/LKOH.json").mock(
            return_value=respx.MockResponse(200, json=MOEX_SHARE_JSON)
        )

        # Вызываем синхронную функцию
        share = get_share("LKOH")

        assert isinstance(share, Share)
        assert share.sec_id == "SBER"
