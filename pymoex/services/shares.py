from pymoex.models.share import Share
from pymoex.utils.table import parse_table
from pymoex.core import endpoints


class SharesService:
    """Сервис для получения данных по акциям Московской биржи."""

    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_share(self, ticker: str) -> Share:
        """
        Получить информацию по акции.

        :param ticker: тикер акции (например, 'SBER')
        :return: модель Share
        """
        ticker = ticker.upper()
        cache_key = f"share:{ticker}"

        async def _fetch():
            return await self._load_share(ticker)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=None)

    async def _load_share(self, ticker: str) -> Share:
        """Загрузка данных по акции напрямую из MOEX ISS API."""
        data = await self.session.get(
            endpoints.share(ticker)
        )

        if not data["securities"]["data"]:
            raise ValueError(f"Security {ticker} not found")

        sec = parse_table(data["securities"])[0]

        md_list = parse_table(data.get("marketdata", {}))
        md = next((r for r in md_list if r.get("BOARDID") == "TQBR"), None)

        last_price, open_price, high_price, low_price = self._extract_prices(md)

        return Share(
            # Идентификация
            secid=sec.get("SECID"),
            shortname=sec.get("SHORTNAME"),
            secname=sec.get("SECNAME"),
            isin=sec.get("ISIN"),
            reg_number=sec.get("REGNUMBER"),

            # Цены
            last_price=last_price,
            prev_price=sec.get("PREVPRICE"),
            prev_waprice=sec.get("PREVWAPRICE"),
            prev_legal_close_price=sec.get("PREVLEGALCLOSEPRICE"),
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,

            # Параметры торгов
            currency_id=sec.get("CURRENCYID"),
            min_step=sec.get("MINSTEP"),
            decimals=sec.get("DECIMALS"),
            settle_date=sec.get("SETTLEDATE"),

            # Лоты и объём
            lot_size=sec.get("LOTSIZE"),
            face_value=sec.get("FACEVALUE"),
            issue_size=sec.get("ISSUESIZE"),

            # Статус и листинг
            status=sec.get("STATUS"),
            list_level=sec.get("LISTLEVEL"),
            sec_type=sec.get("SECTYPE"),

            # Классификация
            board_id=md.get("BOARDID") if md else sec.get("BOARDID"),
            board_name=md.get("BOARDNAME") if md else sec.get("BOARDNAME"),
            sector_id=sec.get("SECTORID"),
            market_code=sec.get("MARKETCODE"),
            instr_id=sec.get("INSTRID"),
        )

    @staticmethod
    def _extract_prices(md: dict | None):
        if not md:
            return None, None, None, None
        return (
            md.get("LAST") or md.get("WAPRICE"),
            md.get("OPEN"),
            md.get("HIGH"),
            md.get("LOW"),
        )
