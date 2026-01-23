from pymoex.models.share import Share
from pymoex.utils.table import parse_table
from pymoex.core import endpoints


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
            raise ValueError(f"Security {ticker} not found")

        # Таблица securities -> список словарей
        sec = parse_table(data["securities"])[0]

        # Таблица marketdata может содержать данные по нескольким бордам
        md_list = parse_table(data.get("marketdata", {}))

        # Выбираем основную торговую площадку (обычно TQBR)
        md = next((r for r in md_list if r.get("BOARDID") == "TQBR"), None)

        # Извлекаем цены с fallback-логикой
        last_price, open_price, high_price, low_price = self._extract_prices(md)

        # Формируем доменную модель
        return Share(
            # --- Идентификация ---
            sec_id=sec.get("SECID"),
            shortname=sec.get("SHORTNAME"),
            sec_name=sec.get("SECNAME"),
            is_in=sec.get("ISIN"),
            reg_number=sec.get("REGNUMBER"),

            # --- Цены и торговля ---
            last_price=last_price,
            prev_price=sec.get("PREVPRICE"),
            prev_wa_price=sec.get("PREVWAPRICE"),
            prev_legal_close_price=sec.get("PREVLEGALCLOSEPRICE"),
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,

            # --- Валюта и шаг цены ---
            currency_id=sec.get("CURRENCYID"),
            min_step=sec.get("MINSTEP"),
            decimals=sec.get("DECIMALS"),
            settle_date=sec.get("SETTLEDATE"),

            # --- Лоты и объём выпуска ---
            lot_size=sec.get("LOTSIZE"),
            face_value=sec.get("FACEVALUE"),
            issue_size=sec.get("ISSUESIZE"),

            # --- Статус и листинг ---
            status=sec.get("STATUS"),
            list_level=sec.get("LISTLEVEL"),
            sec_type=sec.get("SECTYPE"),

            # --- Классификация и рынок ---
            board_id=md.get("BOARDID") if md else sec.get("BOARDID"),
            board_name=md.get("BOARDNAME") if md else sec.get("BOARDNAME"),
            sector_id=sec.get("SECTORID"),
            market_code=sec.get("MARKETCODE"),
            instr_id=sec.get("INSTRID"),
        )

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
            md.get("OPEN"),                      # цена открытия
            md.get("HIGH"),                      # максимум дня
            md.get("LOW"),                       # минимум дня
        )
