import logging
from abc import ABC, abstractmethod
from typing import ClassVar, cast

from pydantic import BaseModel

from pymoex.core.interfaces import ICache
from pymoex.core.session import MoexSession
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.utils.boards import select_best_board
from pymoex.utils.response import (
    find_row_by_board,
    get_table,
    normalize_ticker,
)
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)


class BaseService:
    def __init__(self, session: MoexSession, cache: ICache) -> None:
        self.session: MoexSession = session
        self.cache: ICache = cache


class InstrumentService[TModel: BaseModel](BaseService, ABC):
    instrument_name: ClassVar[str]
    cache_prefix: ClassVar[str]
    ttl: ClassVar[int]
    priority_boards_attr: ClassVar[str]

    @abstractmethod
    def get_model(self) -> type[TModel]:
        """Возвращает Pydantic-модель инструмента."""
        ...

    @abstractmethod
    def get_endpoint(self, ticker: str) -> str:
        """Возвращает endpoint MOEX ISS для инструмента."""
        ...

    async def get(self, ticker: str) -> TModel:
        ticker = normalize_ticker(ticker)
        cache_key = f"{self.cache_prefix}:{ticker}"

        async def _fetch() -> TModel:
            data = await self.session.get(self.get_endpoint(ticker))
            return self._build_instrument(ticker, data)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=self.ttl)

    def _build_instrument(self, ticker: str, data: dict[str, object]) -> TModel:
        securities = get_table(data, "securities")

        if not securities.get("data"):
            logger.warning(
                "%s %s not found in MOEX response",
                self.instrument_name,
                ticker,
            )
            raise InstrumentNotFoundError(f"{self.instrument_name} {ticker} not found")

        sec_rows = parse_table(securities)
        md_rows = parse_table(get_table(data, "marketdata"))
        yield_rows = parse_table(get_table(data, "marketdata_yields"))

        if not sec_rows:
            logger.warning(
                "%s %s has empty securities table",
                self.instrument_name,
                ticker,
            )
            raise InstrumentNotFoundError(f"{self.instrument_name} {ticker} not found")

        priority_boards = cast(
            list[str],
            getattr(self.session.settings, self.priority_boards_attr),
        )

        target_board = select_best_board(
            sec_rows=sec_rows,
            md_rows=md_rows,
            priority_boards=priority_boards,
        )

        logger.debug(
            "Selected board %r for %s %s",
            target_board,
            self.instrument_name.lower(),
            ticker,
        )

        security = find_row_by_board(sec_rows, target_board) or sec_rows[0]
        market_data = find_row_by_board(md_rows, target_board) or {}
        yield_data = find_row_by_board(yield_rows, target_board) or {}

        combined_data = {**security, **yield_data, **market_data}

        return self.get_model().model_validate(combined_data)
