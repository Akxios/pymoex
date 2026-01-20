from pydantic import BaseModel
from typing import Optional
from datetime import date


class Bond(BaseModel):
    """
    Модель облигации Московской биржи.
    Содержит справочные данные, параметры купона и доходности.
    """

    # Идентификация
    secid: str
    shortname: str
    secname: Optional[str] = None
    isin: Optional[str] = None
    reg_number: Optional[str] = None

    # Цена и доходность
    last_price: Optional[float] = None
    prev_waprice: Optional[float] = None
    prev_price: Optional[float] = None
    prev_legal_close_price: Optional[float] = None
    yiel_dat_prevwa_price: Optional[float] = None
    yield_percent: Optional[float] = None

    # Купоны
    coupon_value: Optional[float] = None
    coupon_percent: Optional[float] = None
    accrued_int: Optional[float] = None
    next_coupon: Optional[date] = None

    # Срок обращения
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
