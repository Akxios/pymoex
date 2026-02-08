"""
Константы для работы с API Московской биржи (ISS).
Значения групп (group_name) взяты из официального справочника:
https://iss.moex.com/iss/index.json (блок securitygroups)
"""

# --- РЫНОК АКЦИЙ (Equity) ---
MOEX_SHARE_GROUPS = {
    "stock_shares",  # Основные акции
    "stock_foreign_shares",  # Иностранные акции
    "stock_dr",  # Депозитарные расписки
}

# --- ФОНДЫ (ETFs и ПИФы) ---
MOEX_FUND_GROUPS = {
    "stock_etf",  # Биржевые фонды
    "stock_ppif",  # Паи ПИФов
}

# --- РЫНОК ОБЛИГАЦИЙ ---
MOEX_BOND_GROUPS = {
    "stock_bonds",  # Основная группа
    "stock_eurobond",  # Еврооблигации
}

# --- ВАЛЮТНЫЙ РЫНОК ---
MOEX_CURRENCY_GROUPS = {
    "currency_selt",  # Биржевая валюта
    "currency_metal",  # Драгоценные металлы
    "currency_indices",  # Валютные фиксинги
    "currency_otcindices",  # Внебиржевые валютные индексы
}

# --- СРОЧНЫЙ РЫНОК  ---
MOEX_FUTURES_GROUPS = {
    "futures_forts",  # Фьючерсы
    "futures_options",  # Опционы на фьючерсы
    "currency_futures",  # Валютные фьючерсы
}

# --- ИНДЕКСЫ ---
MOEX_INDEX_GROUPS = {
    "stock_index",  # Индексы акций
}

# --- СПЕЦИФИЧЕСКИЕ И ПРОЧИЕ ИНСТРУМЕНТЫ ---
# Обычно не нужны в общем поиске, но могут пригодиться
MOEX_SPECIAL_GROUPS = {
    "stock_deposit",  # Депозиты с ЦК (Денежный рынок)
    "stock_qnv",  # Инструменты для квалифицированных инвесторов
    "stock_gcc",  # Клиринговые сертификаты участия (КСУ)
    "stock_mortgage",  # Ипотечные сертификаты
}

# --- КОМБИНИРОВАННЫЕ ГРУППЫ (Для удобства поиска) ---

# Если пользователь ищет "Акции", он скорее всего хочет видеть и Фонды тоже
ALL_EQUITY_SEARCH = MOEX_SHARE_GROUPS | MOEX_FUND_GROUPS
