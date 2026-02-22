"""
Набор вспомогательных функций для формирования URL эндпоинтов MOEX ISS API.

Используется сервисами (SharesService, BondsService, SearchService и т.д.)
для централизованного построения путей.
"""

# Базовый движок рынка (акции и облигации находятся в engine=stock)
ENGINE = "stock"

# Общий префикс для всех рынков внутри движка
BASE = f"/engines/{ENGINE}/markets"


def share(ticker: str) -> str:
    """
    Эндпоинт для получения информации по акции.

    :param ticker: торговый код акции (например, 'SBER')
    :return: путь вида /engines/stock/markets/shares/securities/{ticker}.json
    """
    return f"{BASE}/shares/securities/{ticker}.json"


def bond(ticker: str) -> str:
    """
    Эндпоинт для получения информации по облигации.

    :param ticker: ISIN или торговый код облигации (например, 'RU000A10DS74')
    :return: путь вида /engines/stock/markets/bonds/securities/{ticker}.json
    """
    return f"{BASE}/bonds/securities/{ticker}.json"


def search() -> str:
    """
    Эндпоинт глобального поиска по всем инструментам MOEX.

    Используется для поиска по тикеру, названию, ISIN, эмитенту и т.д.

    :return: путь /securities.json
    """
    return "/securities.json"


def dividends(ticker: str) -> str:
    """
    Эндпоинт для получения истории и будущих дивидендов по акции.

    :param ticker: торговый код акции (например, 'SBER')
    :return: путь вида /securities/{ticker}/dividends.json
    """
    return f"/securities/{ticker}/dividends.json"


def bondization(ticker: str) -> str:
    """
    Эндпоинт для получения купонов, амортизации и оферт по облигации.

    :param ticker: ISIN или торговый код облигации (например, 'RU000A10DS74')
    :return: путь вида /securities/{ticker}/bondization.json
    """
    return f"/securities/{ticker}/bondization.json"
