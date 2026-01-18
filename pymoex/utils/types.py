from datetime import date
from typing import Optional


def safe_date(value: str | None) -> Optional[date]:
    """
    Преобразует строку даты из MOEX API в корректное значение.

    MOEX иногда возвращает фиктивную дату '0000-00-00' или None.
    В таких случаях функция возвращает None, чтобы Pydantic
    и типы Python не падали с ошибкой.

    :param value: строка даты в формате 'YYYY-MM-DD' или None
    :return: date или None
    """
    if not value or value == "0000-00-00":
        return None

    return date.fromisoformat(value)
