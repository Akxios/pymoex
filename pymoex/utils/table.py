from collections.abc import Mapping
from typing import cast


def parse_table(block: Mapping[str, object]) -> list[dict[str, object]]:
    """
    Преобразует MOEX-таблицу (формат {columns: [...], data: [...]})
    в плоский список словарей.

    Гарантирует безопасный парсинг даже при битом или пустом ответе API.
    """
    columns = block.get("columns")
    data = block.get("data")

    if not isinstance(columns, list) or not isinstance(data, list):
        return []

    col_names: list[str] = [str(c) for c in columns]
    result: list[dict[str, object]] = []

    data_list: list[object] = cast(list[object], data)

    for row in data_list:
        if isinstance(row, list):
            row_items: list[object] = cast(list[object], row)

            result.append(dict(zip(col_names, row_items)))

    return result


def first_row(block: Mapping[str, object]) -> dict[str, object] | None:
    """
    Возвращает первую строку MOEX-таблицы в виде словаря.

    Returns:
        Словарь с данными первой строки, либо None, если таблица пуста.
    """
    columns: object | None = block.get("columns")
    data: object | None = block.get("data")

    if not isinstance(columns, list) or not isinstance(data, list) or not data:
        return None

    data_list: list[object] = cast(list[object], data)

    first: object = data_list[0]

    if not isinstance(first, list):
        return None

    col_names: list[str] = [str(c) for c in columns]

    first_items: list[object] = cast(list[object], first)

    return dict(zip(col_names, first_items))


__all__ = ["parse_table", "first_row"]
