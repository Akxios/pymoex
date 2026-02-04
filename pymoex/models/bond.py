from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from pymoex.utils.types import safe_date


class Bond(BaseModel):
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

    model_config = ConfigDict(
        populate_by_name=True,  # принимать sec_id и SECID
        extra="ignore",  # MOEX любит лишние поля (тут главное не плакать)
    )

    def __repr__(self) -> str:
        """
        Короткое человекочитаемое представление облигации
        для логов, консоли и отладки.
        """
        parts = [self.sec_id]

        if self.short_name:
            parts.append(self.short_name)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        if self.effective_yield is not None:
            parts.append(f"yield={self.effective_yield}%")

        return f"<Bond {' | '.join(parts)}>"

    def __str__(self) -> str:
        return self.__repr__()

    # --- Вычисляемые свойства ---
    @computed_field
    @property
    def last_price(self) -> Optional[float]:
        """
        Последняя цена облигации без НКД (clean price) в валюте номинала.
        """
        if self.price_percent is None or self.face_value is None:
            return None
        return self.face_value * self.price_percent / 100

    @computed_field
    @property
    def last_dirty_price(self) -> Optional[float]:
        """
        Последняя полная цена облигации (с НКД).
        """
        clean = self.last_price
        if clean is None:
            return None

        return clean + (self.accruedint or 0)

    # --- Идентификация инструмента ---
    sec_id: str = Field(alias="SECID")  # торговый код / ISIN
    short_name: str = Field(alias="SHORTNAME")  # краткое название
    sec_name: Optional[str] = Field(None, alias="SECNAME")
    isin: Optional[str] = Field(None, alias="ISIN")  # ISIN
    reg_number: Optional[str] = Field(None, alias="REGNUMBER")

    # --- Рыночные показатели ---
    price_percent: Optional[float] = None  # последняя цена, %
    effective_yield: Optional[float] = Field(None)  # эффективная доходность, %

    # --- Купонные параметры ---
    coupon_value: Optional[float] = Field(None, alias="COUPONVALUE")
    coupon_percent: Optional[float] = Field(None, alias="COUPONPERCENT")
    accruedint: Optional[float] = Field(None, alias="ACCRUEDINT")  # НКД
    next_coupon: Optional[date] = Field(
        None, alias="NEXTCOUPON"
    )  # дата следующего купона

    # --- Сроки обращения ---
    mat_date: Optional[date] = Field(None, alias="MATDATE")  # дата погашения
    coupon_period: Optional[int] = Field(
        None, alias="COUPONPERIOD"
    )  # периодичность купона (дни)
    date_yield_from_issuer: Optional[date] = Field(
        None, alias="DATEYIELDFROMISSUER"
    )  # дата начала расчёта доходности

    # --- Номинал и расчёт лотов ---
    face_value: Optional[float] = Field(None, alias="FACEVALUE")
    lot_size: Optional[int] = Field(None, alias="LOTSIZE")
    lot_value: Optional[float] = Field(None, alias="LOTVALUE")
    face_unit: Optional[str] = Field(None, alias="FACEUNIT")
    currency_id: Optional[str] = Field(None, alias="CURRENCYID")

    # --- Ликвидность и листинг ---
    issue_size_placed: Optional[int] = Field(None, alias="ISSUESIZEPLACED")
    list_level: Optional[int] = Field(None, alias="LISTLEVEL")
    status: Optional[str] = Field(None, alias="STATUS")
    sec_type: Optional[str] = Field(None, alias="SECTYPE")

    # --- Опции: оферты, выкуп ---
    offer_date: Optional[date] = Field(None, alias="OFFERDATE")
    call_option_date: Optional[date] = Field(None, alias="CALLOPTIONDATE")
    put_option_date: Optional[date] = Field(None, alias="PUTOPTIONDATE")
    buyback_date: Optional[date] = Field(None, alias="BUYBACKDATE")
    buyback_price: Optional[float] = Field(None, alias="BUYBACKPRICE")

    # --- Классификация ---
    bond_type: Optional[str] = Field(None, alias="BONDTYPE")
    bond_sub_type: Optional[str] = Field(None, alias="BONDSUBTYPE")
    sector_id: Optional[str] = Field(None, alias="SECTORID")

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
