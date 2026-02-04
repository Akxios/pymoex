from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.share import Share
from pymoex.utils.table import parse_table


class SharesService:
    """
    Сервис для получения данных по акциям Московской биржи.

    Отвечает за:
    - загрузку справочных и торговых данных по акциям
    - выбор основной торговой площадки (TQBR)
    - нормализацию ответа ISS
    - преобразование в модель Share
    - кэширование результатов
    """

    def __init__(self, session, cache):
        # Асинхронная HTTP-сессия (MoexSession)
        self.session = session

        # TTL-кэш для цен и справочных данных
        self.cache = cache

    async def get_share(self, ticker: str) -> Share:
        """
        Получить информацию по акции.

        :param ticker: тикер акции (например, 'SBER')
        :return: экземпляр модели Share
        """
        ticker = ticker.upper()
        cache_key = f"share:{ticker}"

        async def _fetch():
            return await self._load_share(ticker)

        # Атомарно получить из кэша или загрузить из ISS
        return await self.cache.get_or_set(cache_key, _fetch, ttl=None)

    async def _load_share(self, ticker: str) -> Share:
        """
        Загрузка данных по акции напрямую из MOEX ISS API.

        Выполняет:
        1. Запрос справочной информации
        2. Запрос рыночных данных
        3. Выбор основной торговой доски (TQBR)
        4. Формирование доменной модели Share
        """
        data = await self.session.get(endpoints.share(ticker))

        # Проверяем, что бумага существует
        if not data["securities"]["data"]:
            raise InstrumentNotFoundError(f"Share {ticker} not found")

        # Таблица securities -> список словарей
        sec_list = parse_table(data["securities"])

        sec = next(
            (r for r in sec_list if r.get("BOARDID") == "TQBR"),
            sec_list[0],  # fallback
        )

        # Таблица marketdata может содержать данные по нескольким бордам
        md_list = parse_table(data.get("marketdata", {}))

        # Выбираем основную торговую площадку
        md = next((r for r in md_list if r.get("BOARDID") == "TQBR"), None)

        # Извлекаем цены с fallback-логикой
        last_price, open_price, high_price, low_price = self._extract_prices(md)

        data = {
            **sec,
            "last_price": last_price,
            "open_price": open_price,
            "high_price": high_price,
            "low_price": low_price,
        }

        return Share.model_validate(data)

    @staticmethod
    def _extract_prices(md: dict | None):
        """
        Извлекает основные цены из marketdata с приоритетом:
        LAST -> WAPRICE для последней цены.
        """
        if not md:
            return None, None, None, None

        return (
            md.get("LAST") or md.get("WAPRICE"),  # последняя цена
            md.get("OPEN"),  # цена открытия
            md.get("HIGH"),  # максимум дня
            md.get("LOW"),  # минимум дня
        )
