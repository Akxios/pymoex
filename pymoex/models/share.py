from datetime import date
from typing import Optional

from pydantic import BaseModel


class Share(BaseModel):
    """
    Модель акции Московской биржи.

    Содержит:
    - идентификационные данные
    - текущие и исторические цены
    - параметры торгов
    - информацию о листинге и классификации
    """

    def __repr__(self) -> str:
        """
        Короткое человекочитаемое представление акции
        для логов, консоли и отладки.
        """
        parts = [self.sec_id]

        if self.short_name:
            parts.append(self.short_name)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        return f"<Share {' | '.join(parts)}>"

    def __str__(self) -> str:
        return self.__repr__()

    # --- Идентификация ---
    sec_id: str  # торговый код
    short_name: str  # краткое название
    sec_name: Optional[str] = None
    isin: Optional[str] = None  # ISIN
    reg_number: Optional[str] = None

    # --- Цены и торговые параметры ---
    last_price: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None

    # --- Валюта и шаг цены ---
    currency_id: Optional[str] = None
    min_step: Optional[float] = None
    decimals: Optional[int] = None
    settle_date: Optional[date] = None

    # --- Лоты и объём выпуска ---
    lot_size: Optional[int] = None
    face_value: Optional[float] = None
    issue_size: Optional[int] = None

    # --- Статус и листинг ---
    status: Optional[str] = None
    list_level: Optional[int] = None
    sec_type: Optional[str] = None

    # --- Классификация и рынок ---
    board_id: Optional[str] = None
    board_name: Optional[str] = None
    sector_id: Optional[str] = None
    market_code: Optional[str] = None
    instr_id: Optional[str] = None
