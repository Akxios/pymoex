from enum import Enum


class InstrumentType(str, Enum):
    """
    Тип финансового инструмента.

    Используется в поиске и фильтрации:
    - SHARE — акции
    - BOND — облигации
    """

    SHARE = "share"
    BOND = "bond"
