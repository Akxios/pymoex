from pydantic import BaseModel
from typing import Optional
from datetime import date


class Bond(BaseModel):
    """
    Модель облигации Московской биржи.
    Содержит справочные данные, параметры купона и доходности.
    """

    def __repr__(self) -> str:
        parts = [self.sec_id]

        if self.shortname:
            parts.append(self.shortname)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        if self.yield_percent is not None:
            parts.append(f"yield={self.yield_percent}%")

        return f"<Bond {' | '.join(parts)}>"

    def __str__(self) -> str:
        return self.__repr__()

    # Идентификация
    sec_id: str
    shortname: str
    sec_name: Optional[str] = None
    is_in: Optional[str] = None
    reg_number: Optional[str] = None

    # Цена и доходность
    last_price: Optional[float] = None
    yield_percent: Optional[float] = None

    # Купоны
    coupon_value: Optional[float] = None
    coupon_percent: Optional[float] = None
    accrued_int: Optional[float] = None
    next_coupon: Optional[date] = None

    # Сроки
    mat_date: Optional[date] = None
    coupon_period: Optional[int] = None
    date_yield_from_issuer: Optional[date] = None

    # Номинал и лоты
    face_value: Optional[float] = None
    lot_size: Optional[int] = None
    lot_value: Optional[float] = None
    face_unit: Optional[str] = None
    currency_id: Optional[str] = None

    # Ликвидность и листинг
    issue_size_placed: Optional[int] = None
    list_level: Optional[int] = None
    status: Optional[str] = None
    sec_type: Optional[str] = None

    # Опции (оферты, выкуп)
    offer_date: Optional[date] = None
    calloption_date: Optional[date] = None
    put_option_date: Optional[date] = None
    buyback_date: Optional[date] = None
    buyback_price: Optional[float] = None

    # Классификация
    bond_type: Optional[str] = None
    bond_sub_type: Optional[str] = None
    sector_id: Optional[str] = None
