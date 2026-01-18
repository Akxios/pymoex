class SearchService:
    """Сервис поиска инструментов на Московской бирже."""

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def find(self, query: str, instrument_type: str | None = None) -> list[dict]:
        """
        Поиск инструментов по строке.

        :param query: строка поиска (тикер, название, ISIN)
        :param instrument_type: 'share', 'bond' или None (все инструменты)
        :return: список найденных инструментов в виде словарей
        """
        cache_key = f"search:{query}:{instrument_type or 'all'}"

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        data = await self.session.get(
            "/securities.json",
            params={"q": query, "limit": 1000}
        )

        columns = data["securities"]["columns"]
        rows = data["securities"]["data"]
        result = [dict(zip(columns, row)) for row in rows]

        if instrument_type == "share":
            result = [r for r in result if r.get("group") == "stock_shares"]
        elif instrument_type == "bond":
            result = [r for r in result if r.get("group") == "stock_bonds"]

        await self.cache.set(cache_key, result)
        return result
