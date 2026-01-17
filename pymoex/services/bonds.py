from pymoex.models.bond import Bond
from pymoex.utils.table import first_row
from pymoex.utils.types import safe_date


class BondsService:
    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_bond(self, ticker: str) -> Bond:
        cache_key = f"share:{ticker}"

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        share = await self._load_bond(ticker)

        await self.cache.set(cache_key, share)
        return share

    async def _load_bond(self, ticker: str) -> Bond:
        search = await self.session.get("/securities.json", params={"q": ticker})
        cols = search["securities"]["columns"]
        rows = search["securities"]["data"]

        sec = next((dict(zip(cols, r)) for r in rows if r[0] == ticker), None)
        if not sec:
            raise ValueError(f"Bond {ticker} not found")

        market = await self.session.get(
            f"/engines/stock/markets/bonds/securities/{ticker}.json"
        )

        sec = first_row(market["securities"])
        md = first_row(market["marketdata"])
        yld = first_row(market["marketdata_yields"])

        return Bond(
            secid=sec.get("SECID"),
            shortname=sec.get("SHORTNAME"),
            secname=sec.get("SECNAME"),
            isin=sec.get("ISIN"),
            regnumber=sec.get("REGNUMBER"),

            last_price=(
                    md.get("LAST")
                    or md.get("WAPRICE")
                    or md.get("MARKETPRICE")
                    or md.get("PREVLEGALCLOSEPRICE")
            ),

            yield_percent=yld.get("EFFECTIVEYIELD") if yld else None,

            couponvalue=sec.get("COUPONVALUE"),
            couponpercent=sec.get("COUPONPERCENT"),
            accruedint=sec.get("ACCRUEDINT"),
            nextcoupon=safe_date(sec.get("NEXTCOUPON")),

            matdate=safe_date(sec.get("MATDATE")),
            couponperiod=sec.get("COUPONPERIOD"),
            dateyieldfromissuer=safe_date(sec.get("DATEYIELDFROMISSUER")),

            facevalue=sec.get("FACEVALUE"),
            lotsize=sec.get("LOTSIZE"),
            lotvalue=sec.get("LOTVALUE"),
            faceunit=sec.get("FACEUNIT"),
            currencyid=sec.get("CURRENCYID"),

            issuesizeplaced=sec.get("ISSUESIZEPLACED"),
            listlevel=sec.get("LISTLEVEL"),
            status=sec.get("STATUS"),
            sectype=sec.get("SECTYPE"),

            offerdate=safe_date(sec.get("OFFERDATE")),
            calloptiondate=safe_date(sec.get("CALLOPTIONDATE")),
            putoptiondate=safe_date(sec.get("PUTOPTIONDATE")),
            buybackdate=safe_date(sec.get("BUYBACKDATE")),
            buybackprice=sec.get("BUYBACKPRICE"),

            bondtype=sec.get("BONDTYPE"),
            bondsubtype=sec.get("BONDSUBTYPE"),
            sectorid=sec.get("SECTORID"),
        )
