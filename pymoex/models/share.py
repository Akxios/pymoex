from pydantic import BaseModel
from typing import Optional
from datetime import date


class Share(BaseModel):
    """
    Модель акции Московской биржи.
    Содержит как справочную информацию, так и торговые параметры.
    """

    def __repr__(self) -> str:
        parts = [self.sec_id]

        if self.shortname:
            parts.append(self.shortname)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        return f"<Share {' | '.join(parts)}>"

    def __str__(self) -> str:
        return self.__repr__()

    # Идентификация
    sec_id: str
    shortname: str
    sec_name: Optional[str] = None
    is_in: Optional[str] = None
    reg_number: Optional[str] = None

    # Цены и торговля
    last_price: Optional[float] = None
    prev_price: Optional[float] = None
    prev_wa_price: Optional[float] = None
    prev_legal_close_price: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None

    # Валюта и шаг цены
    currency_id: Optional[str] = None
    min_step: Optional[float] = None
    decimals: Optional[int] = None
    settle_date: Optional[date] = None

    # Лоты и объём выпуска
    lot_size: Optional[int] = None
    face_value: Optional[float] = None
    issue_size: Optional[int] = None

    # Статус и листинг
    status: Optional[str] = None
    list_level: Optional[int] = None
    sec_type: Optional[str] = None

    # Классификация
    board_id: Optional[str] = None
    board_name: Optional[str] = None
    sector_id: Optional[str] = None
    market_code: Optional[str] = None
    instr_id: Optional[str] = None
