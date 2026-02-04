from datetime import date
from typing import Optional

from pydantic import Field, computed_field

from .base import BaseInstrument


class Share(BaseInstrument):
    """
    Акция Московской биржи.

    Содержит:
    - идентификационные данные
    - текущие и исторические цены
    - параметры торгов
    - информацию о листинге и классификации

    Пример:
        Share(SECID="SBER", SHORTNAME="Сбербанк", LAST=250.5)
    """

    # --- Идентификация ---
    sec_id: str = Field(alias="SECID", description="Торговый код инструмента (SECID)")
    short_name: str = Field(
        alias="SHORTNAME", description="Краткое название инструмента"
    )
    sec_name: Optional[str] = Field(
        None, alias="SECNAME", description="Полное официальное наименование"
    )
    isin: Optional[str] = Field(
        None,
        alias="ISIN",
        description="Международный идентификатор ценной бумаги (ISIN)",
    )
    reg_number: Optional[str] = Field(
        None, alias="REGNUMBER", description="Регистрационный номер бумаги"
    )

    # --- Цены ---
    prev_price: Optional[float] = Field(
        None, alias="PREVPRICE", description="Предыдущая цена"
    )
    prev_weighted_price: Optional[float] = Field(
        None, alias="PREVWAPRICE", description="Предыдущая средневзвешенная цена"
    )
    prev_close_price: Optional[float] = Field(
        None,
        alias="PREVLEGALCLOSEPRICE",
        description="Официальная цена закрытия предыдущего дня",
    )
    close_price: Optional[float] = Field(
        None, alias="CLOSEPRICE", description="Цена закрытия"
    )

    last_price: Optional[float] = Field(
        None, alias="LAST", description="Последняя цена сделки"
    )
    open_price: Optional[float] = Field(None, alias="OPEN", description="Цена открытия")
    high_price: Optional[float] = Field(
        None, alias="HIGH", description="Максимальная цена"
    )
    low_price: Optional[float] = Field(
        None, alias="LOW", description="Минимальная цена"
    )

    # --- Параметры ---
    currency_id: Optional[str] = Field(
        None, alias="CURRENCYID", description="Валюта торгов"
    )
    min_step: Optional[float] = Field(None, alias="MINSTEP", description="Шаг цены")
    decimals: Optional[int] = Field(
        None, alias="DECIMALS", description="Знаков после запятой"
    )
    settle_date: Optional[date] = Field(
        None, alias="SETTLEDATE", description="Дата расчёта"
    )

    lot_size: Optional[int] = Field(
        None, alias="LOTSIZE", description="Размер лота (бумаг)"
    )
    face_value: Optional[float] = Field(
        None, alias="FACEVALUE", description="Номинальная стоимость бумаги"
    )
    issue_size: Optional[int] = Field(
        None, alias="ISSUESIZE", description="Объём эмиссии"
    )

    # --- Статус ---
    status: Optional[str] = Field(
        None, alias="STATUS", description="Статус инструмента"
    )
    list_level: Optional[int] = Field(
        None, alias="LISTLEVEL", description="Уровень листинга"
    )
    sec_type: Optional[str] = Field(None, alias="SECTYPE", description="Тип бумаги")

    # --- Рынок ---
    board_id: Optional[str] = Field(None, alias="BOARDID", description="Код площадки")
    board_name: Optional[str] = Field(
        None, alias="BOARDNAME", description="Название площадки"
    )
    sector_id: Optional[str] = Field(None, alias="SECTORID", description="Сектор")
    market_code: Optional[str] = Field(
        None, alias="MARKETCODE", description="Код рынка"
    )
    instr_id: Optional[str] = Field(None, alias="INSTRID", description="ID инструмента")

    # --- Computed ---
    @computed_field
    @property
    def reference_price(self) -> Optional[float]:
        """Базовая цена для сравнения."""
        return self.prev_weighted_price or self.prev_price

    @computed_field
    @property
    def effective_close(self) -> Optional[float]:
        """Фактическая цена закрытия."""
        return self.close_price or self.prev_close_price

    # --- Repr ---
    def __repr__(self) -> str:
        parts = [self.sec_id]
        if self.short_name:
            parts.append(self.short_name)
        if self.last_price is not None:
            parts.append(f"price={self.last_price}")
        return f"<Share {' | '.join(parts)}>"
