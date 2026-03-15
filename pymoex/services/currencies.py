import logging

from pymoex.core import endpoints
from pymoex.exceptions import InstrumentNotFoundError
from pymoex.models.currency import Currency
from pymoex.utils.boards import select_best_board
from pymoex.utils.table import parse_table

logger = logging.getLogger(__name__)

# Словарь удобных псевдонимов для самых популярных валют и металлов
CURRENCY_ALIASES = {
    "USD": "USD000UTSTOM",  # Классический биржевой доллар (торги приостановлены)
    "USDCB": "USDRUBTOMOTC",  # Внебиржевой индекс (актуальный курс после санкций)
    "EUR": "EUR_RUB__TOM",  # Классический биржевой евро (торги приостановлены)
    "EURCB": "EURRUBTOMOTC",  # Внебиржевой индекс евро
    "CNY": "CNYRUB_TOM",  # Юань
    "HKD": "HKDRUB_TOM",  # Гонконгский доллар
    "TRY": "TRYRUB_TOM",  # Турецкая лира
    "BYN": "BYNRUB_TOM",  # Белорусский рубль
    "KZT": "KZTRUB_TOM",  # Казахстанский тенге
    "GLD": "GLDRUB_TOM",  # Золото (торгуется в валютной секции!)
    "SLV": "SLVRUB_TOM",  # Серебро
}


class CurrenciesService:
    def __init__(self, session, cache):
        self.session = session
        self.cache = cache

    async def get_currency(self, ticker: str) -> Currency:
        ticker = ticker.upper()

        real_ticker = CURRENCY_ALIASES.get(ticker, ticker)

        cache_key = f"currency:{real_ticker}"

        async def _fetch():
            return await self._load_currency(real_ticker)

        return await self.cache.get_or_set(cache_key, _fetch, ttl=60)

    async def _load_currency(self, ticker: str) -> Currency:
        # Рынки, в которых мы будем искать валюту
        markets_to_try = ["selt", "otcindices"]
        data = None

        for market in markets_to_try:
            current_data = await self.session.get(
                endpoints.currency(ticker, market=market)
            )

            if current_data.get("securities", {}).get("data"):
                data = current_data
                break

        # Если перебрали все рынки, а данных так и нет
        if not data or not data.get("securities", {}).get("data"):
            logger.warning(f"Currency {ticker} not found in MOEX response")
            raise InstrumentNotFoundError(f"Currency {ticker} not found")

        sec_rows = parse_table(data["securities"])
        md_rows = parse_table(data.get("marketdata", {}))

        priority_boards = self.session.settings.preferred_currency_boards

        target_board = select_best_board(
            sec_rows=sec_rows, md_rows=md_rows, priority_boards=priority_boards
        )

        logger.debug(f"Selected board '{target_board}' for currency {ticker}")

        security = next(
            (r for r in sec_rows if r["BOARDID"] == target_board), sec_rows[0]
        )
        market_data = next((r for r in md_rows if r["BOARDID"] == target_board), {})

        combined_data = {**security, **market_data}
        return Currency.model_validate(combined_data)
