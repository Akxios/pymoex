from pymoex.models.share import Share
from pymoex.utils.table import parse_table


class SharesService:
    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_share(self, ticker: str) -> Share:
        cache_key = f"share:{ticker}"

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        share = await self._load_share(ticker)

        await self.cache.set(cache_key, share)
        return share

    async def _load_share(self, ticker: str) -> Share:
        data = await self.session.get(
            f"/engines/stock/markets/shares/securities/{ticker}.json"
        )

        if not data["securities"]["data"]:
            raise ValueError(f"Security {ticker} not found")

        sec = parse_table(data["securities"])[0]

        md_block = data.get("marketdata", {})
        md_columns = md_block.get("columns", [])
        md_rows = md_block.get("data", [])

        marketdata = [dict(zip(md_columns, row)) for row in md_rows if row]

        md = next((row for row in marketdata if row.get("BOARDID") == "TQBR"), None)

        last_price = None
        open_price = None
        high_price = None
        low_price = None

        if md:
            last_price = md.get("LAST") or md.get("WAPRICE")
            open_price = md.get("OPEN")
            high_price = md.get("HIGH")
            low_price = md.get("LOW")

        return Share(
            secid=sec.get("SECID"),
            shortname=sec.get("SHORTNAME"),
            secname=sec.get("SECNAME"),
            isin=sec.get("ISIN"),
            regnumber=sec.get("REGNUMBER"),

            last_price=last_price,
            prevprice=sec.get("PREVPRICE"),
            prevwaprice=sec.get("PREVWAPRICE"),
            prevlegalcloseprice=sec.get("PREVLEGALCLOSEPRICE"),
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,

            currencyid=sec.get("CURRENCYID"),
            minstep=sec.get("MINSTEP"),
            decimals=sec.get("DECIMALS"),
            settledate=sec.get("SETTLEDATE"),

            lotsize=sec.get("LOTSIZE"),
            facevalue=sec.get("FACEVALUE"),
            issuesize=sec.get("ISSUESIZE"),

            status=sec.get("STATUS"),
            listlevel=sec.get("LISTLEVEL"),
            sectype=sec.get("SECTYPE"),

            boardid=md.get("BOARDID") if md else sec.get("BOARDID"),
            boardname=md.get("BOARDNAME") if md else sec.get("BOARDNAME"),
            sectorid=sec.get("SECTORID"),
            marketcode=sec.get("MARKETCODE"),
            instrid=sec.get("INSTRID"),
        )
