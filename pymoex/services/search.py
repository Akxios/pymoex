import logging

from pymoex.core import endpoints
from pymoex.core.constants import (
    BOND_GROUPS,
    CURRENCY_GROUPS,
    FUND_GROUPS,
    SHARE_GROUPS,
    CacheTTL,
)
from pymoex.models.enums import InstrumentType
from pymoex.models.search import Search
from pymoex.services.base import BaseService
from pymoex.utils.response import get_table
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)

type Row = dict[str, object]

GROUPS_BY_INSTRUMENT_TYPE = {
    InstrumentType.SHARE: SHARE_GROUPS,
    InstrumentType.FUND: FUND_GROUPS,
    InstrumentType.BOND: BOND_GROUPS,
    InstrumentType.CURRENCY: CURRENCY_GROUPS,
}


class SearchService(BaseService):
    """
    Сервис для поиска инструментов
    """

    async def find(
        self,
        query: str,
        instrument_type: InstrumentType | str | None = None,
    ) -> list[Search]:
        query_norm = query.strip().lower()

        if not query_norm:
            return []

        itype = self._normalize_instrument_type(instrument_type)

        logger.debug("Search query=%r type=%s", query_norm, itype)

        cache_key = f"search:{query_norm}:{itype.value if itype else 'all'}"

        async def _fetch() -> list[Search]:
            data = await self.session.get(
                endpoints.search(),
                params={"q": query_norm, "limit": 1000},
            )

            raw = parse_table(get_table(data, "securities"))

            logger.debug("MOEX returned %s raw item for %r", len(raw), query_norm)

            filtered = self._filter_by_type(raw, itype)

            if len(filtered) != len(raw):
                logger.debug(
                    "Filtered by type %s: %s -> %s",
                    itype,
                    len(raw),
                    len(filtered),
                )

            ranked = self._rank_results(filtered, query_norm)

            if not ranked and filtered:
                logger.debug(
                    "Ranking removed all results for %r; no strict matches",
                    query_norm,
                )

            unique = self._deduplicate_by_secid(ranked)

            results = [Search.model_validate(row) for row in unique]

            logger.debug(
                "Found %s unique results for %r",
                len(results),
                query_norm,
            )

            return results

        return await self.cache.get_or_set(
            cache_key,
            _fetch,
            ttl=CacheTTL.SEARCH_TTL_SECONDS,
        )

    @staticmethod
    def _filter_by_type(
        raw: list[Row],
        itype: InstrumentType | None,
    ) -> list[Row]:
        if itype is None:
            return raw

        allowed_groups = GROUPS_BY_INSTRUMENT_TYPE.get(itype)

        if allowed_groups is None:
            return []

        return [row for row in raw if row.get("group") in allowed_groups]

    @staticmethod
    def _normalize_instrument_type(
        value: InstrumentType | str | None,
    ) -> InstrumentType | None:
        if value is None:
            return None

        if isinstance(value, InstrumentType):
            return value

        try:
            return InstrumentType(value.strip().lower())
        except ValueError as e:
            raise ValueError(f"Unknown instrument type: {value!r}") from e

    @staticmethod
    def _rank_results(raw: list[Row], query: str) -> list[Row]:
        def norm(value: object) -> str:
            return value.lower().replace(" ", "") if isinstance(value, str) else ""

        q = norm(query)

        def score(row: Row) -> int:
            secid = norm(row.get("secid"))
            short_name = norm(row.get("shortname"))
            isin = norm(row.get("isin"))
            full_name = norm(row.get("name"))

            if secid == q or isin == q:
                return 100
            if short_name == q:
                return 90
            if q in secid:
                return 80
            if q in short_name:
                return 70
            if q in full_name:
                return 65

            return 0

        scored = [(score(row), row) for row in raw]
        scored = [(points, row) for points, row in scored if points > 0]

        scored.sort(
            key=lambda item: (
                item[0],
                -len(norm(item[1].get("secid"))),
            ),
            reverse=True,
        )

        return [row for _, row in scored][: CacheTTL.COUNT_RESULTS]

    @staticmethod
    def _deduplicate_by_secid(raw: list[Row]) -> list[Row]:
        unique: dict[str, Row] = {}

        for row in raw:
            secid = row.get("secid")

            if not isinstance(secid, str):
                continue

            key = secid.upper()

            if key not in unique:
                unique[key] = row

        return list(unique.values())
