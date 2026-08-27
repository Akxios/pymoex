from collections.abc import Mapping
from typing import cast

from pymoex.exceptions import MoexResponseParseError


def parse_table(block: Mapping[str, object]) -> list[dict[str, object]]:
    """
    Преобразует MOEX-таблицу в плоский список словарей.
    Проверяет структуру таблицы и строк без потери значений.
    """
    columns = block.get("columns")
    data = block.get("data")

    if not isinstance(columns, list):
        raise MoexResponseParseError("Expected 'columns' to be a list")

    if not isinstance(data, list):
        raise MoexResponseParseError("Expected 'data' to be a list")

    columns_list = cast(list[object], columns)
    data_list = cast(list[object], data)

    if not all(isinstance(column, str) for column in columns_list):
        raise MoexResponseParseError("Expected all column names to be strings")

    col_names = cast(list[str], columns_list)
    result: list[dict[str, object]] = []

    for index, row in enumerate(data_list):
        if not isinstance(row, list):
            raise MoexResponseParseError(f"Row {index} is not a list")

        row_items = cast(list[object], row)

        if len(row_items) != len(col_names):
            raise MoexResponseParseError(
                f"Row {index} has {len(row_items)} values, expected {len(col_names)}"
            )

        result.append(dict(zip(col_names, row_items, strict=True)))

    return result


def first_row(block: Mapping[str, object]) -> dict[str, object] | None:
    """
    Возвращает первую строку MOEX-таблицы в виде словаря.
    """
    rows = parse_table(block)
    return rows[0] if rows else None


__all__ = ["parse_table", "first_row"]
