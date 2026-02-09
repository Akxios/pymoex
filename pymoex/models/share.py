from decimal import Decimal
from typing import Optional

from pydantic import Field, computed_field

from pymoex.utils.types import MoexDate, MoexDecimal, MoexInt

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
    name: str = Field(
        alias="SECNAME", description="Полное официальное наименование акции"
    )
    isin: str = Field(
        alias="ISIN",
        description="Международный идентификатор ценной бумаги (ISIN)",
    )
    reg_number: str = Field(
        alias="REGNUMBER", description="Регистрационный номер бумаги акции"
    )

    # --- Цены ---
    prev_price: MoexDecimal = Field(
        None, alias="PREVPRICE", description="Предыдущая цена"
    )
    prev_weighted_price: MoexDecimal = Field(
        None, alias="PREVWAPRICE", description="Предыдущая средневзвешенная цена"
    )
    prev_close_price: MoexDecimal = Field(
        None,
        alias="PREVLEGALCLOSEPRICE",
        description="Официальная цена закрытия предыдущего дня",
    )
    close_price: MoexDecimal = Field(
        None, alias="CLOSEPRICE", description="Цена закрытия"
    )

    last_price: MoexDecimal = Field(
        None, alias="LAST", description="Последняя цена сделки"
    )
    open_price: MoexDecimal = Field(None, alias="OPEN", description="Цена открытия")
    high_price: MoexDecimal = Field(None, alias="HIGH", description="Максимальная цена")
    low_price: MoexDecimal = Field(None, alias="LOW", description="Минимальная цена")

    # --- Объемы торгов ---
    volume_today: MoexInt = Field(
        None, alias="VOLTODAY", description="Объем торгов в штуках"
    )
    value_today: MoexDecimal = Field(
        None, alias="VALTODAY", description="Объем торгов в валюте (руб)"
    )
    num_trades: MoexInt = Field(
        None, alias="NUMTRADES", description="Количество сделок"
    )

    # --- Параметры ---
    currency_id: Optional[str] = Field(
        None, alias="CURRENCYID", description="Валюта торгов"
    )
    min_step: MoexDecimal = Field(None, alias="MINSTEP", description="Шаг цены")
    decimals: MoexInt = Field(
        None, alias="DECIMALS", description="Знаков после запятой"
    )
    settle_date: MoexDate = Field(None, alias="SETTLEDATE", description="Дата расчёта")

    lot_size: MoexInt = Field(None, alias="LOTSIZE", description="Размер лота (бумаг)")
    face_value: MoexDecimal = Field(
        None,
        alias="FACEVALUE",
        description="Номинальная стоимость одной акции",
    )
    issue_size: MoexInt = Field(None, alias="ISSUESIZE", description="Объём эмиссии")

    # --- Статус ---
    status: Optional[str] = Field(
        None, alias="STATUS", description="Статус инструмента"
    )
    list_level: MoexInt = Field(
        None, alias="LISTLEVEL", description="Уровень листинга на бирже"
    )
    sec_type: Optional[str] = Field(
        None, alias="SECTYPE", description="Тип ценной бумаги"
    )

    # --- Рынок ---
    board_id: Optional[str] = Field(None, alias="BOARDID", description="Код площадки")
    board_name: Optional[str] = Field(
        None, alias="BOARDNAME", description="Название площадки"
    )
    sector_id: Optional[str] = Field(
        None, alias="SECTORID", description="Идентификатор сектора экономики"
    )
    market_code: Optional[str] = Field(
        None, alias="MARKETCODE", description="Код рынка"
    )
    instr_id: Optional[str] = Field(None, alias="INSTRID", description="ID инструмента")

    # --- Computed ---
    @computed_field
    @property
    def reference_price(self) -> Optional[Decimal]:
        """Базовая цена для сравнения."""
        return self.prev_weighted_price or self.prev_price

    @computed_field
    @property
    def effective_close(self) -> Optional[Decimal]:
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


__all__ = ["Share"]
