from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field


class Share(BaseModel):
    """
    Модель акции Московской биржи.

    Содержит:
    - идентификационные данные
    - текущие и исторические цены
    - параметры торгов
    - информацию о листинге и классификации
    """

    model_config = ConfigDict(
        populate_by_name=True,  # принимать sec_id и SECID
        extra="ignore",  # MOEX любит лишние поля (тут главное не плакать)
    )

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

    # def __str__(self) -> str:
    # return self.__repr__()

    # --- Идентификация ---
    sec_id: str = Field(alias="SECID")  # торговый код
    short_name: str = Field(alias="SHORTNAME")  # краткое название
    sec_name: Optional[str] = Field(None, alias="SECNAME")
    isin: Optional[str] = Field(None, alias="ISIN")  # ISIN
    reg_number: Optional[str] = Field(None, alias="REGNUMBER")

    # --- Цены и торговые параметры ---
    prev_price: Optional[float] = Field(None, alias="PREVPRICE")
    prev_weighted_price: Optional[float] = Field(None, alias="PREVWAPRICE")
    prev_close_price: Optional[float] = Field(None, alias="PREVLEGALCLOSEPRICE")
    close_price: Optional[float] = Field(None, alias="CLOSEPRICE")

    last_price: Optional[float] = Field(None, alias="LAST")
    open_price: Optional[float] = Field(None, alias="OPEN")
    high_price: Optional[float] = Field(None, alias="HIGH")
    low_price: Optional[float] = Field(None, alias="LOW")

    # --- Валюта и шаг цены ---
    currency_id: Optional[str] = Field(None, alias="CURRENCYID")
    min_step: Optional[float] = Field(None, alias="MINSTEP")
    decimals: Optional[int] = Field(None, alias="DECIMALS")
    settle_date: Optional[date] = Field(None, alias="SETTLEDATE")

    # --- Лоты и объём выпуска ---
    lot_size: Optional[int] = Field(None, alias="LOTSIZE")
    face_value: Optional[float] = Field(None, alias="FACEVALUE")
    issue_size: Optional[int] = Field(None, alias="ISSUESIZE")

    # --- Статус и листинг ---
    status: Optional[str] = Field(None, alias="STATUS")
    list_level: Optional[int] = Field(None, alias="LISTLEVEL")
    sec_type: Optional[str] = Field(None, alias="SECTYPE")

    # --- Классификация и рынок ---
    board_id: Optional[str] = Field(None, alias="BOARDID")
    board_name: Optional[str] = Field(None, alias="BOARDNAME")
    sector_id: Optional[str] = Field(None, alias="SECTORID")
    market_code: Optional[str] = Field(None, alias="MARKETCODE")
    instr_id: Optional[str] = Field(None, alias="INSTRID")

    @computed_field
    @property
    def reference_price(self) -> Optional[float]:
        """
        Базовая цена для сравнения и расчёта изменений.
        """
        return self.prev_weighted_price or self.prev_price

    @computed_field
    @property
    def effective_close(self) -> Optional[float]:
        """
        Цена закрытия: сегодняшняя, если сессия завершена,
        иначе — вчерашняя официальная.
        """
        return self.close_price or self.prev_close_price
