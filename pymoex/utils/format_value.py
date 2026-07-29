from decimal import Decimal

from pymoex.models.search import Search


def format_value(value: object | None, suffix: str | None = None) -> str:
    """
    Красиво форматирует значение для вывода в консоль.
    """
    if value is None:
        return "—"

    if isinstance(value, Decimal):
        text = f"{value:.4f}".rstrip("0").rstrip(".")
    else:
        text = str(value)

    if suffix:
        return f"{text} {suffix}"

    return text


def format_search(title: str, results: list[Search], limit: int = 5) -> None:
    """
    Красиво печатает результаты поиска.
    """
    print(f"\n--- {title} ---")

    if not results:
        print("Ничего не найдено.")
        return

    for item in results[:limit]:
        name = item.name or item.short_name or "—"
        print(f" - {name} ({item.sec_id}) | group={item.group}")
