from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.share import Share
from pymoex.utils.table import parse_table


class SharesService:
    """
    Сервис для получения данных по акциям.
    """

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_share(self, ticker: str) -> Share:
        ticker = ticker.upper()
        cache_key = f"share:{ticker}"

        async def _fetch():
            return await self._load_share(ticker)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=60)

    async def _load_share(self, ticker: str) -> Share:
        data = await self.session.get(endpoints.share(ticker))

        if not data.get("securities", {}).get("data"):
            raise InstrumentNotFoundError(f"Share {ticker} not found")

        # 1. Парсим таблицы
        sec_rows = parse_table(data["securities"])
        md_rows = parse_table(data.get("marketdata", {}))

        # 2. Ищем лучшую запись в securities (Приоритет: TQBR -> Первая попавшаяся)
        security = next(
            (row for row in sec_rows if row.get("BOARDID") == "TQBR"), sec_rows[0]
        )

        # Запоминаем, какой board_id мы выбрали
        target_board = security.get("BOARDID")

        # 3. Ищем соответствующие рыночные данные для этого же борда
        market_data = next(
            (row for row in md_rows if row.get("BOARDID") == target_board),
            {},  # Если рыночных данных нет, возвращаем пустой dict
        )

        # 4. Объединяем данные
        combined_data = {**market_data, **security}

        # 5. Отдаем Pydantic
        return Share.model_validate(combined_data)
