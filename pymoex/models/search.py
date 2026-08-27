from typing import override

from pydantic import Field

from .base import BaseInstrument


class Search(BaseInstrument):
    """
    Модель результата глобального поиска по инструментам Московской биржи.

    Позволяет идентифицировать актив, найти его основной режим торгов (board)
    и получить регистрационные данные эмитента. Используется как первый шаг
    перед запросом детальной информации по конкретному тикеру.
    """

    # --- Идентификаторы ---
    sec_id: str = Field(alias="secid")
    """Тикер"""

    short_name: str = Field(alias="shortname")
    """Краткое название"""

    name: str | None = Field(default=None, alias="name")
    """Полное название"""

    isin: str | None = Field(default=None, alias="isin")
    """ISIN (Международный идентификационный код)"""

    reg_number: str | None = Field(default=None, alias="regnumber")
    """Регистрационный номер (для акций/облигаций)"""

    # --- Классификация ---
    type: str | None = Field(default=None, alias="type")
    """Тип бумаги (например, common_share, corporate_bond)"""

    group: str | None = Field(default=None, alias="group")
    """Группа инструмента (например, stock_shares, stock_bonds)"""

    # --- Торговые данные ---
    is_traded: bool | None = Field(default=None, alias="is_traded")
    """Признак того, торгуется ли сейчас инструмент"""

    primary_boardid: str | None = Field(default=None, alias="primary_boardid")
    """Главный режим торгов (например, TQBR)"""

    marketprice_boardid: str | None = Field(default=None, alias="marketprice_boardid")
    """Режим торгов для расчета рыночной цены"""

    # --- Эмитент (Компания) ---
    emitent_id: int | None = Field(default=None, alias="emitent_id")
    """Внутренний ID эмитента на бирже"""

    emitent_title: str | None = Field(default=None, alias="emitent_title")
    """Юридическое название эмитента"""

    emitent_inn: str | None = Field(default=None, alias="emitent_inn")
    """ИНН эмитента"""

    emitent_okpo: str | None = Field(default=None, alias="emitent_okpo")
    """ОКПО эмитента"""

    # --- Repr ---
    @override
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление результата поиска."""
        # Выбираем наиболее полное имя для отображения
        display_name = self.name or self.short_name

        # Собираем части для консистентного вывода
        parts: list[str] = [self.sec_id]

        if self.isin:
            parts.append(self.isin)

        parts.append(display_name)

        if self.group:
            parts.append(f"group={self.group}")

        if self.is_traded is True:
            status = "Active"
        elif self.is_traded is False:
            status = "Inactive"
        else:
            status = "Unknown"

        parts.append(status)

        return f"<Search | {' | '.join(parts)}>"

    # --- Str ---
    @override
    def __str__(self) -> str:
        return repr(self)


__all__ = ["Search"]
