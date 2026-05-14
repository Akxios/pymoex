"""
Константы для работы с API Московской биржи (ISS).

Значения группвзяты из официального справочника:
https://iss.moex.com/iss/index.json (блок securitygroups)
"""

type GroupName = str

SHARE_GROUPS: frozenset[GroupName] = frozenset(
    {
        "stock_shares",  # Основные акции
        "stock_foreign_shares",  # Иностранные акции
        "stock_dr",  # Депозитарные расписки
    }
)


FUND_GROUPS: frozenset[GroupName] = frozenset(
    {
        "stock_etf",  # Биржевые фонды
        "stock_ppif",  # Паи ПИФов
    }
)


BOND_GROUPS: frozenset[GroupName] = frozenset(
    {
        "stock_bonds",  # Основная группа
        "stock_eurobond",  # Еврооблигации
    }
)


CURRENCY_GROUPS: frozenset[GroupName] = frozenset(
    {
        "currency_selt",  # Биржевая валюта
        "currency_metal",  # Драгоценные металлы
        "currency_indices",  # Валютные фиксинги
        "currency_otcindices",  # Внебиржевые валютные индексы
    }
)


FUTURES_GROUPS: frozenset[GroupName] = frozenset(
    {
        "futures_forts",  # Фьючерсы
        "futures_options",  # Опционы на фьючерсы
        "currency_futures",  # Валютные фьючерсы
    }
)


INDEX_GROUPS: frozenset[GroupName] = frozenset(
    {
        "stock_index",  # Индексы акций
    }
)

SPECIAL_GROUPS: frozenset[GroupName] = frozenset(
    {
        "stock_deposit",  # Депозиты с ЦК
        "stock_qnv",  # Инструменты для квалифицированных инвесторов
        "stock_gcc",  # Клиринговые сертификаты участия
        "stock_mortgage",  # Ипотечные сертификаты
    }
)

EQUITY_SEARCH_GROUPS: frozenset[GroupName] = SHARE_GROUPS | FUND_GROUPS


DEFAULT_SEARCH_GROUPS: frozenset[GroupName] = (
    SHARE_GROUPS
    | FUND_GROUPS
    | BOND_GROUPS
    | CURRENCY_GROUPS
    | FUTURES_GROUPS
    | INDEX_GROUPS
)


class CacheTTL:
    """Время жизни кэша для разных типов данных (в секундах)."""

    BOND_TTL_SECONDS: int = 60
    BOND_EVENTS_TTL_SECONDS: int = 3600

    SHARE_TTL_SECONDS: int = 60
    SHARE_EVENT_TTL_SECONDS: int = 3600

    SEARCH_TTL_SECONDS: int = 300
    COUNT_RESULTS: int = 20

    CURRENCY_TTL_SECONDS: int = 60
