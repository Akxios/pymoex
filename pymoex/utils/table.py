from typing import Any


def parse_table(block: dict) -> list[dict[str, Any]]:
    """
    Преобразует MOEX-таблицу формата:
        { "columns": [...], "data": [[...], [...]] }
    в список словарей.

    :param block: блок ответа ISS API
    :return: список строк в виде словарей
    """
    columns = block["columns"]
    return [dict(zip(columns, row)) for row in block["data"]]


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

    return dict(zip(columns, rows[0]))
