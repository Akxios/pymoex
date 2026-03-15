from typing import Optional

from pydantic import Field

from .base import BaseInstrument


class Search(BaseInstrument):
    """
    Модель результата глобального поиска по инструментам Московской биржи.
    """

    # --- Идентификаторы ---
    sec_id: str = Field(alias="secid")
    """Тикер"""

    short_name: str = Field(alias="shortname")
    """Краткое название"""

    name: Optional[str] = Field(None, alias="name")
    """Полное название"""

    isin: Optional[str] = Field(None, alias="isin")
    """ISIN (Международный идентификационный код)"""

    reg_number: Optional[str] = Field(None, alias="regnumber")
    """Регистрационный номер (для акций/облигаций)"""

    # --- Классификация ---
    type: Optional[str] = Field(None, alias="type")
    """Тип бумаги (например, common_share, corporate_bond)"""

    group: Optional[str] = Field(None, alias="group")
    """Группа инструмента (например, stock_shares, stock_bonds)"""

    # --- Торговые данные ---
    is_traded: Optional[bool] = Field(False, alias="is_traded")
    """Признак того, торгуется ли сейчас инструмент"""

    primary_boardid: Optional[str] = Field(None, alias="primary_boardid")
    """Главный режим торгов (например, TQBR)"""

    marketprice_boardid: Optional[str] = Field(None, alias="marketprice_boardid")
    """Режим торгов для расчета рыночной цены"""

    # --- Эмитент (Компания) ---
    emitent_id: Optional[int] = Field(None, alias="emitent_id")
    """Внутренний ID эмитента на бирже"""

    emitent_title: Optional[str] = Field(None, alias="emitent_title")
    """Юридическое название эмитента"""

    emitent_inn: Optional[str] = Field(None, alias="emitent_inn")
    """ИНН эмитента"""

    emitent_okpo: Optional[str] = Field(None, alias="emitent_okpo")
    """ОКПО эмитента"""

    # --- Repr ---
    def __repr__(self) -> str:
        """Человекочитаемое представление результата поиска."""
        # Защита от None: если полного имени нет, берем краткое
        display_name = self.name or self.short_name

        # Опциональные поля выводим только если они есть
        isin_part = f" | {self.isin}" if self.isin else ""
        group_part = f" | {self.group}" if self.group else ""

        # Более понятный статус на русском
        status = "Торгуется" if self.is_traded else "Не торгуется"

        return f"<Search | {self.sec_id}{isin_part} | {display_name}{group_part} | {status}>"


__all__ = ["Search"]
