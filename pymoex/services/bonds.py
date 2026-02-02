from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.utils.table import first_row
from pymoex.utils.types import safe_date


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
        yield_percent = self._extract_yield(yld)

        return Bond(
            # Идентификация
            sec_id=sec["SECID"],
            short_name=sec["SHORTNAME"],
            sec_name=sec.get("SECNAME"),
            is_in=sec.get("ISIN"),
            reg_number=sec.get("REGNUMBER"),
            # Цена и доходность
            price_percent=self._extract_price_percent(sec),
            yield_percent=yield_percent,
            # Купоны
            coupon_value=sec.get("COUPONVALUE"),
            coupon_percent=sec.get("COUPONPERCENT"),
            accruedint=sec.get("ACCRUEDINT"),
            next_coupon=safe_date(sec.get("NEXTCOUPON")),
            # Сроки
            mat_date=safe_date(sec.get("MATDATE")),
            coupon_period=sec.get("COUPONPERIOD"),
            date_yield_from_issuer=safe_date(sec.get("DATEYIELDFROMISSUER")),
            # Номинал и лоты
            face_value=sec.get("FACEVALUE"),
            lot_size=sec.get("LOTSIZE"),
            lot_value=sec.get("LOTVALUE"),
            face_unit=sec.get("FACEUNIT"),
            currency_id=sec.get("CURRENCYID"),
            # Ликвидность и листинг
            issue_size_placed=sec.get("ISSUESIZEPLACED"),
            list_level=sec.get("LISTLEVEL"),
            status=sec.get("STATUS"),
            sec_type=sec.get("SECTYPE"),
            # Опции
            offer_date=safe_date(sec.get("OFFERDATE")),
            calloption_date=safe_date(sec.get("CALLOPTIONDATE")),
            put_option_date=safe_date(sec.get("PUTOPTIONDATE")),
            buyback_date=safe_date(sec.get("BUYBACKDATE")),
            buyback_price=sec.get("BUYBACKPRICE"),
            # Классификация
            bond_type=sec.get("BONDTYPE"),
            bond_sub_type=sec.get("BONDSUBTYPE"),
            sector_id=sec.get("SECTORID"),
        )

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

    @staticmethod
    def _extract_yield(yld: dict | None) -> float | None:
        if not yld:
            return None
        return yld.get("EFFECTIVEYIELD")
