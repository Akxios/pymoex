import logging

from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)


class BondsService:
    """
    Сервис для получения данных по облигациям.
    """

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_bond(self, ticker: str) -> Bond:
        ticker = ticker.upper()
        cache_key = f"bond:{ticker}"

        async def _fetch():
            return await self._load_bond(ticker)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=60)

    async def _load_bond(self, ticker: str) -> Bond:
        data = await self.session.get(endpoints.bond(ticker))

        if not data.get("securities", {}).get("data"):
            logger.warning(f"Bond {ticker} not found in MOEX response")
            raise InstrumentNotFoundError(f"Bond {ticker} not found")

        # Парсим таблицы
        sec_rows = parse_table(data["securities"])
        md_rows = parse_table(data.get("marketdata", {}))
        yield_rows = parse_table(data.get("marketdata_yields", {}))

        priority_boards = self.session.settings.preferred_bond_boards

        # Смотрим, где есть торговля
        active_boards = {
            row["BOARDID"]
            for row in md_rows
            if (
                row.get("LAST") is not None
                or row.get("LCLOSEPRICE") is not None
                or row.get("LCURRENTPRICE") is not None
            )
        }

        target_board = None

        # Ищем приоритетный борд, который активен
        for board in priority_boards:
            if board in active_boards:
                target_board = board
                break

        # Если приоритетных нет, берем первый активный
        if not target_board and active_boards:
            target_board = list(active_boards)[0]

        # Если торгов нет, ищем по справочнику securities
        if not target_board:
            # Ищем первый борд из списка priority_boards, который есть в sec_rows
            priority_in_sec = [
                r["BOARDID"] for r in sec_rows if r["BOARDID"] in priority_boards
            ]
            target_board = (
                priority_in_sec[0] if priority_in_sec else sec_rows[0]["BOARDID"]
            )

        logger.debug(f"Selected board '{target_board}' for bond {ticker}")

        # Берем данные именно для выбранного борда
        security = next(
            (r for r in sec_rows if r["BOARDID"] == target_board), sec_rows[0]
        )
        market_data = next((r for r in md_rows if r["BOARDID"] == target_board), {})
        yield_data = next((r for r in yield_rows if r["BOARDID"] == target_board), {})

        # Объединяем (statik < yield < market)
        combined_data = {**security, **yield_data, **market_data}

        return Bond.model_validate(combined_data)
