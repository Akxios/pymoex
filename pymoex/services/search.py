from pymoex.core import endpoints
from pymoex.models.enums import InstrumentType
from pymoex.models.search import SearchResult


class SearchService:
    """
    Сервис поиска финансовых инструментов на Московской бирже.

    Позволяет выполнять поиск по:
    - тикеру
    - названию
    - ISIN
    - эмитенту

    Поддерживает фильтрацию по типу инструмента
    (акции, облигации и т.д.).
    """

    def __init__(self, session, cache):
        # Асинхронная HTTP-сессия (MoexSession)
        self.session = session

        # TTL-кэш для результатов поиска
        self.cache = cache

    async def find(
        self,
        query: str,
        instrument_type: InstrumentType | str | None = None,
    ) -> list[SearchResult]:
        """
        Выполнить поиск инструментов по строке.

        :param query: поисковая строка (тикер, название, ISIN, эмитент)
        :param instrument_type: тип инструмента ('share', 'bond' или None)
        :return: список объектов SearchResult
        """
        # Нормализуем запрос
        query_norm = query.strip().lower()

        # Нормализуем тип инструмента
        itype = self._normalize_instrument_type(instrument_type)

        # Ключ кэша учитывает запрос и тип инструмента
        cache_key = f"search:{query_norm}:{itype.value if itype else 'all'}"

        async def _fetch():
            # Запрос к глобальному поисковому эндпоинту ISS
            data = await self.session.get(
                endpoints.search(),
                params={"q": query_norm, "limit": 1000},
            )

            # Преобразуем табличный ответ в список словарей
            columns = data["securities"]["columns"]
            rows = data["securities"]["data"]
            raw = [dict(zip(columns, row)) for row in rows]

            # Фильтрация по типу инструмента
            if itype == InstrumentType.SHARE:
                raw = [r for r in raw if r.get("group") == "stock_shares"]
            elif itype == InstrumentType.BOND:
                raw = [r for r in raw if r.get("group") == "stock_bonds"]

            # Преобразование в доменные модели
            return [SearchResult(**r) for r in raw]

        # Атомарно получить из кэша или выполнить поиск
        return await self.cache.get_or_set(cache_key, _fetch)

    @staticmethod
    def _normalize_instrument_type(
        value: InstrumentType | str | None
    ) -> InstrumentType | None:
        """
        Приводит тип инструмента к перечислению InstrumentType.

        Принимает:
        - InstrumentType
        - строку ('share', 'bond')
        - None
        """
        if value is None:
            return None

        if isinstance(value, InstrumentType):
            return value

        try:
            return InstrumentType(value.lower())
        except ValueError:
            raise ValueError(f"Unknown instrument type: {value!r}")
