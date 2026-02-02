from pymoex.core import endpoints
from pymoex.models.enums import InstrumentType
from pymoex.models.search import SearchResult

BOND_GROUP_PREFIXES = (
    "stock_bond",
    "stock_eurobond",
    "stock_subfederal",
    "stock_municipal",
    "stock_corporate",
)

SHARE_GROUPS = {
    "stock_shares",
}


class SearchService:
    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def find(
        self,
        query: str,
        instrument_type: InstrumentType | str | None = None,
    ) -> list[SearchResult]:
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

            raw = [dict(zip(columns, row)) for row in rows]

            raw = self._filter_by_type(raw, itype)
            raw = self._rank_results(raw, query_norm)

            # убираем дубликаты по SECID
            uniq = {}
            for r in raw:
                secid = r.get("secid")
                if secid:
                    uniq[secid] = r

            return [SearchResult(**r) for r in uniq.values()]

        return await self.cache.get_or_set(cache_key, _fetch)

    def _filter_by_type(
        self,
        raw: list[dict],
        itype: InstrumentType | None,
    ) -> list[dict]:
        if itype is None:
            return raw

        if itype == InstrumentType.SHARE:
            return [r for r in raw if r.get("group") in SHARE_GROUPS]

        if itype == InstrumentType.BOND:
            return [
                r
                for r in raw
                if isinstance(r.get("group"), str) and r["group"].startswith("stock_")
            ]

        return raw

    @staticmethod
    def _normalize_instrument_type(
        value: InstrumentType | str | None,
    ) -> InstrumentType | None:
        if value is None:
            return None

        if isinstance(value, InstrumentType):
            return value

        try:
            return InstrumentType(value.lower())
        except ValueError:
            raise ValueError(f"Unknown instrument type: {value!r}")

    def _rank_results(self, raw: list[dict], query: str) -> list[dict]:
        def norm(s: str | None) -> str:
            return s.lower().replace(" ", "") if isinstance(s, str) else ""

        q = norm(query)

        def score(r: dict) -> int:
            secid = norm(r.get("secid"))
            short = norm(r.get("shortname"))
            isin = norm(r.get("isin"))

            if secid == q or isin == q:
                return 100
            if q in secid:
                return 80
            if q in short:
                return 60
            if all(p in short for p in q.split()):
                return 50
            return 10

        scored = [(score(r), r) for r in raw]
        scored.sort(key=lambda x: x[0], reverse=True)

        return [r for s, r in scored if s > 20][:20]
