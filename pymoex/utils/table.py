from collections.abc import Mapping
from typing import cast


def parse_table(block: Mapping[str, object]) -> list[dict[str, object]]:
    """
    Преобразует MOEX-таблицу в плоский список словарей.
    Гарантирует безопасный парсинг.
    """
    columns = block.get("columns")
    data = block.get("data")

    if not isinstance(columns, list) or not isinstance(data, list):
        return []

    columns_list = cast(list[object], columns)
    data_list = cast(list[object], data)

    col_names = [str(c) for c in columns_list]
    result: list[dict[str, object]] = []

    for row in data_list:
        if isinstance(row, list):
            row_items = cast(list[object], row)
            result.append(dict(zip(col_names, row_items)))

    return result


def first_row(block: Mapping[str, object]) -> dict[str, object] | None:
    """
    Возвращает первую строку MOEX-таблицы в виде словаря.
    """
    columns = block.get("columns")
    data = block.get("data")

    if not isinstance(columns, list) or not isinstance(data, list) or not data:
        return None

    columns_list = cast(list[object], columns)
    data_list = cast(list[object], data)

    first = data_list[0]

    if not isinstance(first, list):
        return None

    col_names = [str(c) for c in columns_list]
    first_items = cast(list[object], first)

    return dict(zip(col_names, first_items))


__all__ = ["parse_table", "first_row"]
