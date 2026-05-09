from datetime import date
from typing import override

from pydantic import Field

from pymoex.utils.types import MoexDecimal

from .base import BaseInstrument


class Dividend(BaseInstrument):
    """
    Модель дивидендной выплаты по акции Московской биржи.

    Атрибуты:
        sec_id: Идентификатор финансового инструмента (Ticker).
        isin: Международный идентификатор (ISIN).
        registry_close_date: Дата фиксации реестра (Record Date).
        value: Размер выплаты на одну акцию.
        currency_id: Валюта выплаты.
    """

    sec_id: str = Field(alias="secid")
    """Идентификатор финансового инструмента"""

    isin: str | None = Field(default=None, alias="isin")
    """ISIN"""

    registry_close_date: date = Field(alias="registryclosedate")
    """Дата закрытия реестра акционеров.)"""

    value: MoexDecimal = Field(alias="value")
    """"Размер дивидендной выплаты на одну акцию в абсолютном выражении."""

    currency_id: str = Field(alias="currencyid")
    """Валюта номинала"""

    # --- Repr ---
    @override
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление дивиденда."""
        parts: list[str] = [self.sec_id]

        if self.isin:
            parts.append(self.isin)

        parts.append(f"close_date={self.registry_close_date}")
        parts.append(f"value={self.value:.2f}")
        parts.append(f"currency={self.currency_id}")

        return f"<Dividend {' | '.join(parts)}>"

    # --- Str ---
    @override
    def __str__(self) -> str:
        return repr(self)


__all__ = ["Dividend"]
