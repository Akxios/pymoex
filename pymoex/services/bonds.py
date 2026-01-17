from pymoex.models.bond import Bond
from pymoex.utils.parsing import first_row

class BondsService:
    def __init__(self, session):
        self.session = session

    async def get_bond(self, ticker: str) -> Bond:
        search = await self.session.get("/securities.json", params={"q": ticker})
        cols = search["securities"]["columns"]
        rows = search["securities"]["data"]

        sec = next(
            (dict(zip(cols, r)) for r in rows if r[0] == ticker),
            None
        )
        if not sec:
            raise ValueError(f"Bond {ticker} not found")

        market = await self.session.get(
            f"/engines/stock/markets/bonds/securities/{ticker}.json"
        )

        md = first_row(market.get("marketdata", {}))
        yld = first_row(market.get("marketdata_yields", {}))

        price = (
                md.get("LAST")
                or md.get("WAPRICE")
                or md.get("MARKETPRICE")
                or md.get("MARKETPRICE2")
                or md.get("PREVLEGALCLOSEPRICE")
        )

        return Bond(
            secid=sec.get("secid"),
            shortname=sec.get("shortname"),
            last_price=price,
            yield_percent=yld.get("EFFECTIVEYIELD"),
        )


