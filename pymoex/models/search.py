from typing import Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    """
    Результат поиска инструмента на Московской бирже.

    Содержит базовую справочную информацию:
    - идентификаторы (SECID, ISIN, регномер)
    - тип и группу инструмента
    - данные об эмитенте
    - торговые площадки
    """

    def __repr__(self) -> str:
        """
        Короткое человекочитаемое представление результата поиска.
        Используется в логах, консоли и отладке.
        """
        # Определяем тип инструмента по группе
        if self.group == "stock_bonds":
            kind = "Bond"
        elif self.group == "stock_shares":
            kind = "Share"
        elif self.group in {"options", "futures_options"}:
            kind = "Option"
        else:
            kind = "Instrument"

        parts = [self.secid]

        if self.shortname:
            parts.append(self.shortname)

        if self.emitent_title:
            parts.append(self.emitent_title)

        if self.is_traded is not None:
            parts.append("traded" if self.is_traded else "not traded")

        return f"<{kind} {' | '.join(parts)}>"

    def __str__(self) -> str:
        return self.__repr__()

    # --- Идентификация ---
    secid: str  # торговый код / ISIN
    shortname: str  # краткое название
    name: str  # полное наименование

    isin: Optional[str] = None
    regnumber: Optional[str] = None

    # --- Тип и рынок ---
    type: Optional[str] = None  # тип бумаги (common_share, corporate_bond и т.п.)
    group: Optional[str] = None  # группа рынка (stock_shares, stock_bonds, options)

    # --- Торговые параметры ---
    is_traded: Optional[bool] = None
    primary_boardid: Optional[str] = None
    marketprice_boardid: Optional[str] = None

    # --- Эмитент ---
    emitent_id: Optional[int] = None
    emitent_title: Optional[str] = None
    emitent_inn: Optional[str] = None
