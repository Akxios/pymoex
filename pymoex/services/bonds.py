from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.utils.table import parse_table


class BondsService:
    """
    Сервис для получения данных по облигациям.
    """

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_bond(self, ticker: str) -> Bond:
        ticker = ticker.upper()
        cache_key = f"bond:{ticker}"

        async def _fetch():
            return await self._load_bond(ticker)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=60)

    async def _load_bond(self, ticker: str) -> Bond:
        data = await self.session.get(endpoints.bond(ticker))

        if not data.get("securities", {}).get("data"):
            raise InstrumentNotFoundError(f"Bond {ticker} not found")

        # 1. Парсим таблицы
        sec_rows = parse_table(data["securities"])

        md_rows = parse_table(data.get("marketdata", {}))
        yield_rows = parse_table(data.get("marketdata_yields", {}))

        # Если тикер не найден или ошибочен, sec_rows может быть пустым
        if not sec_rows:
            raise InstrumentNotFoundError(
                f"Bond {ticker} not found in securities table"
            )

        primary_boards = {"TQOB", "TQCB", "TQOD", "TQIR"}

        # 2. Ищем лучшую запись в securities
        security = next(
            (row for row in sec_rows if row.get("BOARDID") in primary_boards),
            sec_rows[0],
        )

        # Запоминаем, какой board_id мы выбрали
        target_board = security.get("BOARDID")

        # 3. Ищем соответствующие рыночные данные для этого же борда
        market_data = next(
            (row for row in md_rows if row.get("BOARDID") == target_board), {}
        )

        yield_data = next(
            (row for row in yield_rows if row.get("BOARDID") == target_board), {}
        )

        # 4. Объединяем данные
        # Объединяем все три источника.
        combined_data = {**security, **market_data, **yield_data}

        # 5. Отдаем Pydantic
        return Bond.model_validate(combined_data)
