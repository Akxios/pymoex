from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Annotated, Optional

from pydantic import BeforeValidator


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

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_decimal(value) -> Optional[Decimal]:
    """Преобразует строку/число в Decimal, обрабатывая прочерки и пустоты."""
    if value in (None, "", "—", "-"):
        return None

    try:
        if isinstance(value, str):
            value = value.replace(",", ".")

        return Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        return None


def parse_int(value) -> Optional[int]:
    """Преобразует строку в int, обрабатывая прочерки."""
    if value in (None, "", "—", "-"):
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


MoexDate = Annotated[Optional[date], BeforeValidator(safe_date)]
MoexDecimal = Annotated[Optional[Decimal], BeforeValidator(parse_decimal)]
MoexInt = Annotated[Optional[int], BeforeValidator(parse_int)]
