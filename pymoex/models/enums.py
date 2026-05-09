from enum import StrEnum


class InstrumentType(StrEnum):
    """
    Тип финансового инструмента.

    Используется в поиске и фильтрации:
    - SHARE — акции
    - BOND — облигации
    - FUND - фонды
    - CURRENCY - валюта
    """

    SHARE = "share"
    BOND = "bond"
    FUND = "fund"
    CURRENCY = "currency"
