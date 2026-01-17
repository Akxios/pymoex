class SearchService:
    def __init__(self, session):
        self.session = session

    async def find(self, query: str, instrument_type: str | None = None):
        data = await self.session.get(
            "/securities.json",
            params={
                "q": query,
                "limit": 1000
            }
        )

        columns = data["securities"]["columns"]
        rows = data["securities"]["data"]

        result = [dict(zip(columns, row)) for row in rows]

        if instrument_type == "share":
            result = [r for r in result if r.get("group") == "stock_shares"]
        elif instrument_type == "bond":
            result = [r for r in result if r.get("group") == "stock_bonds"]

        return result
