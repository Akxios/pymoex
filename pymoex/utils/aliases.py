_CURRENCY_ALIASES: dict[str, str] = {
    "USD": "USDRUBTOMOTC",  # Внебиржевой доллар
    "EUR": "EURRUBTOMOTC",  # Внебиржевой евро
    "CNY": "CNYRUB_TOM",  # Юань
    "HKD": "HKDRUB_TOM",  # Гонконгский доллар
    "TRY": "TRYRUB_TOM",  # Турецкая лира
    "BYN": "BYNRUB_TOM",  # Белорусский рубль
    "KZT": "KZTRUB_TOM",  # Казахстанский тенге
    "GLD": "GLDRUB_TOM",  # Золото
    "SLV": "SLVRUB_TOM",  # Серебро
    "GOLD": "GLDRUB_TOM",  # Синоним для золота
    "SILVER": "SLVRUB_TOM",  # Синоним для серебра
}


def resolve_currency_secid(query: str) -> str:
    """
    Преобразует пользовательский запрос.
    Если алиас не найден, возвращает запрос как есть.
    """
    normalized_query = query.strip().upper()
    return _CURRENCY_ALIASES.get(normalized_query, normalized_query)


__all__ = ["resolve_currency_secid"]
