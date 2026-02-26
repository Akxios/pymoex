from typing import Any


def parse_table(block: dict) -> list[dict[str, Any]]:
    """
    Преобразует MOEX-таблицу в список словарей.
    """
    columns = block.get("columns", [])
    data = block.get("data", [])
    return [dict(zip(columns, row)) for row in data]


def first_row(block: dict) -> dict[str, Any]:
    """
    Возвращает первую строку MOEX-таблицы в виде словаря.
    Удобно для случаев, когда в таблице гарантированно только одна запись.
    """
    if not block:
        return {}

    columns = block.get("columns", [])
    rows = block.get("data", [])

    if not rows:
        return {}

    return dict(zip(columns, rows[0]))
