from itertools import zip_longest
from typing import Any


def _create_row_dict(columns: list[str], row: list[Any]) -> dict[str, Any]:
    """
    Безопасно связывает колонки и данные.
    Если данных меньше, чем колонок, подставляется None.
    Если данных больше, лишние значения игнорируются (ключ None отфильтровывается).
    """

    return {k: v for k, v in zip_longest(columns, row, fillvalue=None) if k is not None}


def parse_table(block: dict) -> list[dict[str, Any]]:
    """
    Преобразует MOEX-таблицу формата:
        { "columns": [...], "data": [[...], [...]] }
    в список словарей.

    :param block: блок ответа ISS API
    :return: список строк в виде словарей
    """

    columns = block["columns"]
    data = block.get("data", [])
    return [_create_row_dict(columns, row) for row in data]


def first_row(block: dict) -> dict[str, Any]:
    """
    Возвращает первую строку MOEX-таблицы в виде словаря.

    Удобно для случаев, когда в таблице гарантированно
    только одна запись (securities, marketdata и т.п.).

    :param block: блок ответа ISS API
    :return: первая строка или пустой словарь
    """

    if not block:
        return {}

    columns = block.get("columns", [])
    rows = block.get("data", [])

    if not rows:
        return {}

    return _create_row_dict(columns, rows[0])
