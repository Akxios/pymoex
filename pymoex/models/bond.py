from decimal import Decimal
from typing import Optional

from pydantic import Field, computed_field

from pymoex.utils.types import MoexDate, MoexDecimal, MoexInt

from .base import BaseInstrument


class Bond(BaseInstrument):
    """
    Модель облигации Московской биржи.

    Содержит:
    - идентификационные данные бумаги
    - рыночные параметры (цена, доходность)
    - параметры купона
    - даты и сроки обращения
    - номинал и валюту
    - информацию о листинге и ликвидности
    - опционные события (оферты, выкуп)
    """

    # --- Идентификация инструмента ---
    sec_id: str = Field(
        alias="SECID",
        description="Торговый код инструмента на Московской бирже (SECID)",
    )
    short_name: str = Field(alias="SHORTNAME", description="Краткое название облигации")
    sec_name: Optional[str] = Field(
        None, alias="SECNAME", description="Полное официальное наименование облигации"
    )
    isin: Optional[str] = Field(
        None,
        alias="ISIN",
        description="Международный идентификатор ценной бумаги (ISIN)",
    )
    reg_number: Optional[str] = Field(
        None, alias="REGNUMBER", description="Регистрационный номер выпуска облигации"
    )

    # --- Рыночные показатели ---
    price_percent: MoexDecimal = Field(
        None,
        alias="LAST",
        description="Цена облигации в процентах от номинала (clean price, %)",
    )
    effective_yield: MoexDecimal = Field(
        None,
        alias="EFFECTIVEYIELD",
        description="Эффективная доходность облигации, % годовых",
    )

    # --- Купонные параметры ---
    coupon_value: MoexDecimal = Field(
        None, alias="COUPONVALUE", description="Размер купона в валюте номинала"
    )
    coupon_percent: MoexDecimal = Field(
        None, alias="COUPONPERCENT", description="Размер купона в процентах от номинала"
    )
    accruedint: MoexDecimal = Field(
        None, alias="ACCRUEDINT", description="Накопленный купонный доход (НКД)"
    )
    next_coupon: MoexDate = Field(
        None, alias="NEXTCOUPON", description="Дата выплаты следующего купона"
    )

    # --- Сроки обращения ---
    mat_date: MoexDate = Field(
        None, alias="MATDATE", description="Дата погашения облигации"
    )
    coupon_period: MoexInt = Field(
        None, alias="COUPONPERIOD", description="Периодичность выплаты купона в днях"
    )
    date_yield_from_issuer: MoexDate = Field(
        None,
        alias="DATEYIELDFROMISSUER",
        description="Дата начала расчёта доходности по данным эмитента",
    )

    # --- Номинал и расчёт лотов ---
    face_value: MoexDecimal = Field(
        None, alias="FACEVALUE", description="Номинальная стоимость одной облигации"
    )
    lot_size: MoexInt = Field(
        None, alias="LOTSIZE", description="Количество облигаций в одном торговом лоте"
    )
    lot_value: MoexDecimal = Field(
        None, alias="LOTVALUE", description="Стоимость одного лота в валюте номинала"
    )
    face_unit: Optional[str] = Field(
        None, alias="FACEUNIT", description="Единица номинала (например, RUB, USD)"
    )
    currency_id: Optional[str] = Field(
        None, alias="CURRENCYID", description="Код валюты номинала облигации"
    )

    # --- Ликвидность и листинг ---
    issue_size_placed: MoexInt = Field(
        None, alias="ISSUESIZEPLACED", description="Количество размещённых облигаций"
    )
    list_level: MoexInt = Field(
        None, alias="LISTLEVEL", description="Уровень листинга на бирже"
    )
    status: Optional[str] = Field(
        None,
        alias="STATUS",
        description="Cтатус инструмента",
    )
    sec_type: Optional[str] = Field(
        None, alias="SECTYPE", description="Тип ценной бумаги"
    )

    # --- Опции: оферты, выкуп ---
    offer_date: MoexDate = Field(
        None, alias="OFFERDATE", description="Дата оферты по облигации"
    )
    call_option_date: MoexDate = Field(
        None,
        alias="CALLOPTIONDATE",
        description="Дата колл-опциона (право эмитента на выкуп)",
    )
    put_option_date: MoexDate = Field(
        None,
        alias="PUTOPTIONDATE",
        description="Дата пут-опциона (право держателя продать облигацию)",
    )
    buyback_date: MoexDate = Field(
        None, alias="BUYBACKDATE", description="Дата выкупа облигации"
    )
    buyback_price: MoexDecimal = Field(
        None, alias="BUYBACKPRICE", description="Цена выкупа облигации"
    )

    # --- Классификация ---
    bond_type: Optional[str] = Field(
        None, alias="BONDTYPE", description="Основной тип облигации"
    )
    bond_sub_type: Optional[str] = Field(
        None, alias="BONDSUBTYPE", description="Подтип облигации"
    )
    sector_id: Optional[str] = Field(
        None, alias="SECTORID", description="Идентификатор сектора экономики"
    )
    board_id: Optional[str] = Field(None, alias="BOARDID", description="Код площадки")

    # --- Computed ---
    @computed_field
    @property
    def last_price(self) -> Optional[Decimal]:
        """Последняя чистая цена в валюте (Nominal * Price%)."""
        if self.price_percent is None or self.face_value is None:
            return None

        return self.face_value * self.price_percent / Decimal(100)

    @computed_field
    @property
    def last_dirty_price(self) -> Optional[Decimal]:
        """Грязная цена (Clean Price + НКД)."""
        clean = self.last_price

        if clean is None:
            return None

        return clean + (self.accruedint or Decimal(0))

    # --- Repr ---
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление облигации."""
        parts = [self.sec_id]

        if self.short_name:
            parts.append(self.short_name)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        if self.effective_yield is not None:
            parts.append(f"yield={self.effective_yield:.2f}%")

        return f"<Bond {' | '.join(parts)}>"


__all__ = ["Bond"]
