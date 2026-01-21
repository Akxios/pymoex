from pymoex.models.bond import Bond
from pymoex.utils.table import first_row
from pymoex.utils.types import safe_date
from pymoex.core import endpoints


class BondsService:
    """Сервис для получения данных по облигациям MOEX."""

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_bond(self, ticker: str) -> Bond:
        """
        Получить информацию по облигации.

        :param ticker: ISIN или торговый код
        :return: модель Bond
        """
        ticker = ticker.upper()
        cache_key = f"bond:{ticker}"

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        async def _fetch():
            return await self._load_bond(ticker)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=None)

    async def _load_bond(self, ticker: str) -> Bond:
        """Загрузка данных об облигации напрямую из MOEX ISS API."""
        # Поиск в реестре
        data = await self.session.get(
            endpoints.bond(ticker)
        )
        cols = data["securities"]["columns"]
        rows = data["securities"]["data"]

        sec = next((dict(zip(cols, r)) for r in rows if r[0] == ticker), None)
        if not sec:
            raise ValueError(f"Bond {ticker} not found")

        # Рыночные данные
        market = await self.session.get(
            f"/engines/stock/markets/bonds/securities/{ticker}.json"
        )

        sec = first_row(market["securities"])
        md = first_row(market["marketdata"])
        yld = first_row(market["marketdata_yields"])

        last_price = self._extract_price(md)
        yield_percent = self._extract_yield(yld)

        return Bond(
            # Идентификация
            sec_id=sec.get("SECID"),
            shortname=sec.get("SHORTNAME"),
            sec_name=sec.get("SECNAME"),
            is_in=sec.get("ISIN"),
            reg_number=sec.get("REGNUMBER"),

            # Цена и доходность
            last_price=last_price,
            yield_percent=yield_percent,

            # Купоны
            coupon_value=sec.get("COUPONVALUE"),
            coupon_percent=sec.get("COUPONPERCENT"),
            accrued_int=sec.get("ACCRUEDINT"),
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

            # Опции (оферты, выкуп)
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

    @staticmethod
    def _extract_price(md: dict | None) -> float | None:
        if not md:
            return None
        return (
                md.get("LAST")
                or md.get("WAPRICE")
                or md.get("PREVLEGALCLOSEPRICE")
        )

    @staticmethod
    def _extract_yield(yld: dict | None) -> float | None:
        if not yld:
            return None
        return yld.get("EFFECTIVEYIELD")