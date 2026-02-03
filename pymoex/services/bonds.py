from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.utils.table import first_row


class BondsService:
    """
    Сервис для получения данных по облигациям Московской биржи.

    - корректно работает с BOARDID (TQOB / SPOB)
    - берёт цену только из торгового режима
    - использует fallback по цене
    """

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_bond(self, ticker: str) -> Bond:
        ticker = ticker.upper()
        cache_key = f"bond:{ticker}"

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        async def _fetch():
            return await self._load_bond(ticker)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=None)

    async def _load_bond(self, ticker: str) -> Bond:
        registry = await self.session.get(endpoints.bond(ticker))
        r_cols = registry["securities"]["columns"]
        r_rows = registry["securities"]["data"]

        reg_rows = [dict(zip(r_cols, r)) for r in r_rows]
        if not reg_rows:
            raise InstrumentNotFoundError(f"Bond {ticker} not found")
        market = await self.session.get(
            f"/engines/stock/markets/bonds/securities/{ticker}.json"
        )

        m_cols = market["securities"]["columns"]
        m_rows = market["securities"]["data"]
        market_rows = [dict(zip(m_cols, r)) for r in m_rows]

        if not market_rows:
            raise InstrumentNotFoundError(f"Bond {ticker} has no market data")

        sec = self._pick_trading_row(market_rows)
        yld = first_row(market.get("marketdata_yields"))
        effective_yield = yld.get("EFFECTIVEYIELD") if yld else None

        price_percent = self._extract_price_percent(sec)

        data = {
            **sec,
            "price_percent": price_percent,
            "effective_yield": effective_yield,
        }

        return Bond.model_validate(data)

    def _pick_trading_row(self, rows: list[dict]) -> dict:
        """
        Выбор строки торгов:
        1. TQOB — основной рынок
        2. fallback — первая доступная
        """
        for r in rows:
            if r.get("BOARDID") == "TQOB":
                return r
        return rows[0]

    @staticmethod
    def _extract_price_percent(sec: dict) -> float | None:
        """
        Извлечение цены (% от номинала) с fallback.
        """
        return sec.get("PREVWAPRICE") or sec.get("PREVPRICE") or sec.get("MARKETPRICE")
