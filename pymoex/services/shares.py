from pymoex.models.share import Share
from pymoex.utils.parsing import parse_table


class SharesService:
    def __init__(self, session):
        self.session = session

    async def get_share(self, ticker: str) -> Share:
        price = None

        data = await self.session.get(
            f"/engines/stock/markets/shares/securities/{ticker}.json"
        )

        if not data["securities"]["data"]:
            raise ValueError(f"Security {ticker} not found")

        sec = parse_table(data["securities"])[0]

        md_block = data.get("marketdata", {})
        md_columns = md_block.get("columns", [])
        md_rows = md_block.get("data", [])

        marketdata = [
            dict(zip(md_columns, row))
            for row in md_rows
            if row
        ]

        md = next(
            (row for row in marketdata if row.get("BOARDID") == "TQBR"),
            None
        )

        if md:
            price = md.get("LAST") or md.get("WAPRICE")

        return Share(
            secid=sec["SECID"],
            shortname=sec["SHORTNAME"],
            last_price=price,
            open_price=md.get("OPEN") if md else None,
            high_price=md.get("HIGH") if md else None,
            low_price=md.get("LOW") if md else None,
        )
