from datetime import date
from typing import Optional

from pydantic import BaseModel


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

        if self.yield_percent is not None:
            parts.append(f"yield={self.yield_percent}%")

        return f"<Bond {' | '.join(parts)}>"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def last_price(self) -> Optional[float]:
        """
        Последняя цена облигации без НКД (clean price) в валюте номинала.
        """
        if self.price_percent is None or self.face_value is None:
            return None

        return self.face_value * self.price_percent / 100

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
    sec_id: str  # торговый код / ISIN
    short_name: str  # краткое название
    sec_name: Optional[str] = None
    is_in: Optional[str] = None  # ISIN
    reg_number: Optional[str] = None

    # --- Рыночные показатели ---
    price_percent: Optional[float] = None  # последняя цена, %
    yield_percent: Optional[float] = None  # эффективная доходность, %

    # --- Купонные параметры ---
    coupon_value: Optional[float] = None
    coupon_percent: Optional[float] = None
    accruedint: Optional[float] = None  # НКД
    next_coupon: Optional[date] = None  # дата следующего купона

    # --- Сроки обращения ---
    mat_date: Optional[date] = None  # дата погашения
    coupon_period: Optional[int] = None  # периодичность купона (дни)
    date_yield_from_issuer: Optional[date] = None  # дата начала расчёта доходности

    # --- Номинал и расчёт лотов ---
    face_value: Optional[float] = None
    lot_size: Optional[int] = None
    lot_value: Optional[float] = None
    face_unit: Optional[str] = None
    currency_id: Optional[str] = None

    # --- Ликвидность и листинг ---
    issue_size_placed: Optional[int] = None
    list_level: Optional[int] = None
    status: Optional[str] = None
    sec_type: Optional[str] = None

    # --- Опции: оферты, выкуп ---
    offer_date: Optional[date] = None
    calloption_date: Optional[date] = None
    put_option_date: Optional[date] = None
    buyback_date: Optional[date] = None
    buyback_price: Optional[float] = None

    # --- Классификация ---
    bond_type: Optional[str] = None
    bond_sub_type: Optional[str] = None
    sector_id: Optional[str] = None
