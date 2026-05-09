import logging

from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.models.bondization import Amortization, Coupon
from pymoex.utils.boards import select_best_board
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

        target_board = select_best_board(
            sec_rows=sec_rows, md_rows=md_rows, priority_boards=priority_boards
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

    async def get_coupons(self, ticker: str) -> list[Coupon]:
        """
        Получить историю и график будущих купонов по облигации.
        """
        ticker = ticker.upper()
        cache_key = f"coupons:{ticker}"

        async def _fetch():
            data = await self.session.get(endpoints.bondization(ticker))

            if not data.get("coupons", {}).get("data"):
                logger.info(f"No coupons found for {ticker}")
                return []

            rows = parse_table(data["coupons"])
            return [Coupon.model_validate(row) for row in rows]

        # События меняются редко, кэшируем на час
        return await self.cache.get_or_set(cache_key, _fetch, ttl=3600)

    async def get_amortizations(self, ticker: str) -> list[Amortization]:
        """
        Получить график амортизации (выплаты номинала) по облигации.
        """
        ticker = ticker.upper()
        cache_key = f"amortizations:{ticker}"

        async def _fetch():
            data = await self.session.get(endpoints.bondization(ticker))

            if not data.get("amortizations", {}).get("data"):
                logger.info(f"No amortizations found for {ticker}")
                return []

            rows = parse_table(data["amortizations"])
            return [Amortization.model_validate(row) for row in rows]

        return await self.cache.get_or_set(cache_key, _fetch, ttl=3600)
