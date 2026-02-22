from datetime import date
from typing import Optional

from pydantic import Field

from pymoex.utils.types import MoexDecimal

from .base import BaseInstrument


class Dividend(BaseInstrument):
    """
    Модель дивидендной выплаты по акции.
    """

    sec_id: str = Field(alias="secid")
    """Идентификатор финансового инструмента"""

    isin: Optional[str] = Field(default=None, alias="isin")
    """ISIN"""

    registry_close_date: date = Field(alias="registryclosedate")
    """Дата закрытия реестра акционеров.)"""

    value: MoexDecimal = Field(alias="value")
    """"Размер дивидендной выплаты на одну акцию в абсолютном выражении."""

    currency_id: str = Field(alias="currencyid")
    """Валюта номинала"""

    # --- Repr ---
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление дивиденда."""

        return f"<Dividend | {self.sec_id} | close date={self.registry_close_date} | value={self.value} | currency={self.currency_id}>"


__all__ = ["Dividend"]
