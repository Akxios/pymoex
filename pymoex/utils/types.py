import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from logging import Logger
from typing import Annotated

from pydantic import BeforeValidator

logger: Logger = logging.getLogger(name=__name__)


def safe_date(value: object) -> date | None:
    """
    Преобразует строку даты из MOEX API в корректное значение.

    MOEX иногда возвращает фиктивную дату '0000-00-00' или None.
    В таких случаях функция возвращает None, чтобы Pydantic
    и типы Python не падали с ошибкой.

    :param value: строка даты в формате 'YYYY-MM-DD' или None
    :return: date или None
    """
    if value is None:
        return None

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        if not value or value == "0000-00-00":
            return None

        try:
            return date.fromisoformat(value)
        except ValueError:
            logger.warning("Failed to parse date: %r", value)
            return None

    return None


def parse_decimal(value: object) -> Decimal | None:
    """
    Преобразует строку/число в Decimal, обрабатывая прочерки и пустоты
    """
    if value is None:
        return None

    if isinstance(value, str):
        if value.strip() in ("", "—", "-"):
            return None
        value = value.replace(",", ".")

    try:
        return Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        return None


def parse_int(value: object) -> int | None:
    """
    Преобразует строку в int, обрабатывая прочерки
    """
    if value is None:
        return None

    if isinstance(value, str):
        if value.strip() in ("", "—", "-"):
            return None

    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None


type MoexDate = Annotated[date | None, BeforeValidator(func=safe_date)]
type MoexDecimal = Annotated[Decimal | None, BeforeValidator(func=parse_decimal)]
type MoexInt = Annotated[int | None, BeforeValidator(func=parse_int)]

__all__ = ["MoexDate", "MoexDecimal", "MoexInt"]
