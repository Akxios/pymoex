import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Annotated

from pydantic import BeforeValidator

logger = logging.getLogger(__name__)


def safe_date(value: str | None) -> date | None:
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
        logger.warning(f"Failed to parse date: {value!r}")
        return None


def parse_decimal(value) -> Decimal | None:
    """Преобразует строку/число в Decimal, обрабатывая прочерки и пустоты."""
    if value in (None, "", "—", "-"):
        return None

    try:
        if isinstance(value, str):
            value = value.replace(",", ".")

        return Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        return None


def parse_int(value) -> int | None:
    """Преобразует строку в int, обрабатывая прочерки."""
    if value in (None, "", "—", "-"):
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


MoexDate = Annotated[date | None, BeforeValidator(safe_date)]
MoexDecimal = Annotated[Decimal | None, BeforeValidator(parse_decimal)]
MoexInt = Annotated[int | None, BeforeValidator(parse_int)]
