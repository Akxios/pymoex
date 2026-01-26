from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.bond import Bond
from pymoex.utils.table import first_row
from pymoex.utils.types import safe_date


class BondsService:
    """
    Сервис для получения данных по облигациям Московской биржи.

    Отвечает за:
    - загрузку справочных и рыночных данных по облигациям
    - агрегацию данных из разных таблиц ISS
    - преобразование ответа в модель Bond
    - кэширование результатов
    """

    def __init__(self, session, cache):
        # Асинхронная HTTP-сессия (MoexSession)
        self.session = session

        # TTL-кэш для снижения нагрузки на ISS API
        self.cache = cache

    async def get_bond(self, ticker: str) -> Bond:
        """
        Получить информацию по облигации.

        :param ticker: ISIN или торговый код (например, 'RU000A10DS74')
        :return: экземпляр модели Bond
        """
        ticker = ticker.upper()
        cache_key = f"bond:{ticker}"

        # Быстрая попытка взять из кэша
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Фабрика для ленивой загрузки
        async def _fetch():
            return await self._load_bond(ticker)

        # Атомарно получить из кэша или загрузить и сохранить
        return await self.cache.get_or_set(cache_key, _fetch, ttl=None)

    async def _load_bond(self, ticker: str) -> Bond:
        """
        Загрузка данных об облигации напрямую из MOEX ISS API.

        Выполняет:
        1. Поиск бумаги в реестре
        2. Загрузку рыночных данных
        3. Нормализацию и сборку в модель Bond
        """
        # --- 1. Поиск в реестре ценных бумаг ---
        data = await self.session.get(endpoints.bond(ticker))
        cols = data["securities"]["columns"]
        rows = data["securities"]["data"]

        # Преобразуем строки в dict и ищем нужный тикер
        sec = next((dict(zip(cols, r)) for r in rows if r[0] == ticker), None)
        if not sec:
            raise InstrumentNotFoundError(f"Bond {ticker} not found")

        # --- 2. Загрузка рыночных данных ---
        market = await self.session.get(
            f"/engines/stock/markets/bonds/securities/{ticker}.json"
        )

        # Берём первые строки из таблиц
        sec = first_row(market["securities"])
        md = first_row(market["marketdata"])
        yld = first_row(market["marketdata_yields"])

        # Извлекаем цену и доходность с fallback-логикой
        last_price = self._extract_price(md)
        yield_percent = self._extract_yield(yld)

        # --- 3. Формирование доменной модели ---
        return Bond(
            # Идентификация
            sec_id=sec["SECID"],
            short_name=sec["SHORTNAME"],
            sec_name=sec.get("SECNAME"),
            is_in=sec.get("ISIN"),
            reg_number=sec.get("REGNUMBER"),
            # Цена и доходность
            last_price=last_price,
            yield_percent=yield_percent,
            # Купоны
            coupon_value=sec.get("COUPONVALUE"),
            coupon_percent=sec.get("COUPONPERCENT"),
            accrued_int=sec.get("ACCRUEDINT"),
            next_coupon=safe_date(sec.get("NEXTCOUPON")),
            # Сроки
            mat_date=safe_date(sec.get("MATDATE")),
            coupon_period=sec.get("COUPONPERIOD"),
            date_yield_from_issuer=safe_date(sec.get("DATEYIELDFROMISSUER")),
            # Номинал и лоты
            face_value=sec.get("FACEVALUE"),
            lot_size=sec.get("LOTSIZE"),
            lot_value=sec.get("LOTVALUE"),
            face_unit=sec.get("FACEUNIT"),
            currency_id=sec.get("CURRENCYID"),
            # Ликвидность и листинг
            issue_size_placed=sec.get("ISSUESIZEPLACED"),
            list_level=sec.get("LISTLEVEL"),
            status=sec.get("STATUS"),
            sec_type=sec.get("SECTYPE"),
            # Опции (оферты, выкуп)
            offer_date=safe_date(sec.get("OFFERDATE")),
            calloption_date=safe_date(sec.get("CALLOPTIONDATE")),
            put_option_date=safe_date(sec.get("PUTOPTIONDATE")),
            buyback_date=safe_date(sec.get("BUYBACKDATE")),
            buyback_price=sec.get("BUYBACKPRICE"),
            # Классификация
            bond_type=sec.get("BONDTYPE"),
            bond_sub_type=sec.get("BONDSUBTYPE"),
            sector_id=sec.get("SECTORID"),
        )

    @staticmethod
    def _extract_price(md: dict | None) -> float | None:
        """
        Извлечение последней цены с приоритетом:
        LAST -> WAPRICE -> PREVLEGALCLOSEPRICE
        """
        if not md:
            return None

        return md.get("LAST") or md.get("WAPRICE") or md.get("PREVLEGALCLOSEPRICE")

    @staticmethod
    def _extract_yield(yld: dict | None) -> float | None:
        """
        Извлечение эффективной доходности облигации.
        """
        if not yld:
            return None

        return yld.get("EFFECTIVEYIELD")
