"""
Набор вспомогательных функций для формирования URL эндпоинтов MOEX ISS API.
"""

from urllib.parse import quote

STOCK_ENGINE = "stock"
CURRENCY_ENGINE = "currency"

STOCK_MARKET_BASE = f"/engines/{STOCK_ENGINE}/markets"


def _secid(value: str) -> str:
    return quote(value.strip().upper(), safe="")


def share(ticker: str) -> str:
    """
    Эндпоинт для получения информации по акции.
    """
    secid = _secid(ticker)

    return f"{STOCK_MARKET_BASE}/shares/securities/{secid}.json"


def bond(ticker: str) -> str:
    """
    Эндпоинт для получения информации по облигации.
    """

    secid = _secid(ticker)
    return f"{STOCK_MARKET_BASE}/bonds/securities/{secid}.json"


def search() -> str:
    """
    Эндпоинт глобального поиска по всем инструментам MOEX.
    """
    return "/securities.json"


def dividends(ticker: str) -> str:
    """
    Эндпоинт для получения истории и будущих дивидендов по акции.
    """
    secid = _secid(ticker)
    return f"/securities/{secid}/dividends.json"


def bond_events(ticker: str) -> str:
    """
    Эндпоинт для получения купонов, амортизации и оферт по облигации.
    """
    secid = _secid(ticker)
    return f"/securities/{secid}/bondization.json"


def currency(ticker: str, market: str = "selt") -> str:
    """
    Эндпоинт для получения информации по валюте.
    """
    secid = _secid(ticker)
    safe_market = quote(market.strip().lower(), safe="")
    return f"/engines/{CURRENCY_ENGINE}/markets/{safe_market}/securities/{secid}.json"
