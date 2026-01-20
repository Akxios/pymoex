from pymoex.core import endpoints
from pymoex.models.enums import InstrumentType


class SearchService:
    """Сервис поиска инструментов на Московской бирже."""

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def find(
        self,
        query: str,
        instrument_type: InstrumentType | str | None = None,
    ) -> list[dict]:

        query_norm = query.strip().lower()
        itype = self._normalize_instrument_type(instrument_type)
        cache_key = f"search:{query_norm}:{itype.value if itype else 'all'}"

        async def _fetch():
            data = await self.session.get(
                endpoints.search(),
                params={"q": query_norm, "limit": 1000},
            )

            columns = data["securities"]["columns"]
            rows = data["securities"]["data"]
            result = [dict(zip(columns, row)) for row in rows]

            if itype == InstrumentType.SHARE:
                result = [r for r in result if r.get("group") == "stock_shares"]
            elif itype == InstrumentType.BOND:
                result = [r for r in result if r.get("group") == "stock_bonds"]

            return result

        return await self.cache.get_or_set(cache_key, _fetch)

    @staticmethod
    def _normalize_instrument_type(
        value: InstrumentType | str | None
    ) -> InstrumentType | None:
        if value is None:
            return None
        if isinstance(value, InstrumentType):
            return value
        try:
            return InstrumentType(value.lower())
        except ValueError:
            raise ValueError(f"Unknown instrument type: {value!r}")
