from datetime import date
from typing import Optional

from pydantic import Field, computed_field, field_validator

from pymoex.utils.types import safe_date

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

    # --- Рыночные показатели (рассчитываются сервисом) ---
    price_percent: Optional[float] = Field(
        None, description="Цена облигации в процентах от номинала (clean price, %)"
    )
    effective_yield: Optional[float] = Field(
        None, description="Эффективная доходность облигации, % годовых"
    )

    # --- Купонные параметры ---
    coupon_value: Optional[float] = Field(
        None, alias="COUPONVALUE", description="Размер купона в валюте номинала"
    )
    coupon_percent: Optional[float] = Field(
        None, alias="COUPONPERCENT", description="Размер купона в процентах от номинала"
    )
    accruedint: Optional[float] = Field(
        None, alias="ACCRUEDINT", description="Накопленный купонный доход (НКД)"
    )
    next_coupon: Optional[date] = Field(
        None, alias="NEXTCOUPON", description="Дата выплаты следующего купона"
    )

    # --- Сроки обращения ---
    mat_date: Optional[date] = Field(
        None, alias="MATDATE", description="Дата погашения облигации"
    )
    coupon_period: Optional[int] = Field(
        None, alias="COUPONPERIOD", description="Периодичность выплаты купона в днях"
    )
    date_yield_from_issuer: Optional[date] = Field(
        None,
        alias="DATEYIELDFROMISSUER",
        description="Дата начала расчёта доходности по данным эмитента",
    )

    # --- Номинал и расчёт лотов ---
    face_value: Optional[float] = Field(
        None, alias="FACEVALUE", description="Номинальная стоимость одной облигации"
    )
    lot_size: Optional[int] = Field(
        None, alias="LOTSIZE", description="Количество облигаций в одном торговом лоте"
    )
    lot_value: Optional[float] = Field(
        None, alias="LOTVALUE", description="Стоимость одного лота в валюте номинала"
    )
    face_unit: Optional[str] = Field(
        None, alias="FACEUNIT", description="Единица номинала (например, RUB, USD)"
    )
    currency_id: Optional[str] = Field(
        None, alias="CURRENCYID", description="Код валюты номинала облигации"
    )

    # --- Ликвидность и листинг ---
    issue_size_placed: Optional[int] = Field(
        None, alias="ISSUESIZEPLACED", description="Количество размещённых облигаций"
    )
    list_level: Optional[int] = Field(
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
    offer_date: Optional[date] = Field(
        None, alias="OFFERDATE", description="Дата оферты по облигации"
    )
    call_option_date: Optional[date] = Field(
        None,
        alias="CALLOPTIONDATE",
        description="Дата колл-опциона (право эмитента на выкуп)",
    )
    put_option_date: Optional[date] = Field(
        None,
        alias="PUTOPTIONDATE",
        description="Дата пут-опциона (право держателя продать облигацию)",
    )
    buyback_date: Optional[date] = Field(
        None, alias="BUYBACKDATE", description="Дата выкупа облигации"
    )
    buyback_price: Optional[float] = Field(
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

    # --- Валидация дат ---
    @field_validator(
        "next_coupon",
        "mat_date",
        "date_yield_from_issuer",
        "offer_date",
        "call_option_date",
        "put_option_date",
        "buyback_date",
        mode="before",
    )
    @classmethod
    def parse_moex_date(cls, value):
        return safe_date(value)

    # --- Валидация чисел ---
    @field_validator(
        "price_percent",
        "effective_yield",
        "coupon_value",
        "coupon_percent",
        "accruedint",
        "face_value",
        "buyback_price",
        mode="before",
    )
    @classmethod
    def parse_optional_float(cls, value):
        if value in (None, "", "—"):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    # --- Computed ---
    @computed_field
    @property
    def last_price(self) -> Optional[float]:
        """Последняя чистая цена облигации (без НКД) в валюте номинала."""
        if self.price_percent is None or self.face_value is None:
            return None
        return self.face_value * self.price_percent / 100

    @computed_field
    @property
    def last_dirty_price(self) -> Optional[float]:
        """Последняя полная цена облигации (clean price + НКД)."""
        clean = self.last_price
        if clean is None:
            return None
        return clean + (self.accruedint or 0)

    # --- Repr ---
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление облигации."""
        parts = [self.sec_id]

        if self.short_name:
            parts.append(self.short_name)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        if self.effective_yield is not None:
            parts.append(f"yield={self.effective_yield}%")

        return f"<Bond {' | '.join(parts)}>"


__all__ = ["Bond"]
