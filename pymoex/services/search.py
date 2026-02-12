import logging

from pymoex.core import endpoints
from pymoex.core.constants import MOEX_BOND_GROUPS, MOEX_FUND_GROUPS, MOEX_SHARE_GROUPS
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search

logger = logging.getLogger(__name__)


class SearchService:
    """
    Сервис для поиска инструментов
    """

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def find(
        self,
        query: str,
        instrument_type: InstrumentType | str | None = None,
    ) -> list[Search]:
        query_norm = query.strip().lower()
        itype = self._normalize_instrument_type(instrument_type)

        logger.debug(f"Search query='{query_norm}' type={itype}")

        cache_key = f"search:{query_norm}:{itype.value if itype else 'all'}"

        async def _fetch():
            data = await self.session.get(
                endpoints.search(),
                params={"q": query_norm, "limit": 1000},
            )

            sec_data = data.get("securities", {})
            columns = sec_data.get("columns", [])
            rows = sec_data.get("data", [])

            # Превращаем списки в словари
            raw = [dict(zip(columns, row)) for row in rows]

            logger.debug(f"MOEX returned {len(raw)} raw items for '{query_norm}'")

            # Фильтрация по типу
            filtered = self._filter_by_type(raw, itype)

            if len(filtered) != len(raw):
                logger.debug(f"Filtered by type {itype}: {len(raw)} -> {len(filtered)}")

            ranked = self._rank_results(filtered, query_norm)

            if not ranked and filtered:
                logger.debug(
                    f"Ranking removed all results for '{query_norm}' (no strict matches)"
                )

            uniq = {}
            for r in ranked:
                sid = r.get("secid")
                if sid and sid.upper() not in uniq:
                    uniq[sid.upper()] = r

            results = [Search(**r) for r in uniq.values()]

            logger.debug(f"Found {len(results)} unique results for '{query_norm}'")

            return results

        return await self.cache.get_or_set(cache_key, _fetch)

    def _filter_by_type(
        self, raw: list[dict], itype: InstrumentType | None
    ) -> list[dict]:
        if itype is None:
            return raw

        if itype == InstrumentType.SHARE:
            allowed = MOEX_SHARE_GROUPS | MOEX_FUND_GROUPS
            return [r for r in raw if r.get("group") in allowed]

        if itype == InstrumentType.BOND:
            return [r for r in raw if r.get("group") in MOEX_BOND_GROUPS]

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
            full_name = norm(r.get("name"))

            if secid == q or isin == q:
                return 100
            if short == q:
                return 90
            if q in secid:
                return 80
            if q in short:
                return 70
            if q in full_name:
                return 65
            return 0

        # Считаем очки
        scored = [(score(r), r) for r in raw]

        # Оставляем только те, где score > 0
        scored = [x for x in scored if x[0] > 0]

        scored.sort(
            key=lambda x: (x[0], -len(x[1].get("secid", "") or "")), reverse=True
        )

        return [r for s, r in scored][:20]
