from pydantic import BaseModel
from typing import Optional
from datetime import date


class Share(BaseModel):
    """
    Модель акции Московской биржи.
    Содержит как справочную информацию, так и торговые параметры.
    """

    # Идентификация
    secid: str
    shortname: str
    secname: Optional[str] = None
    isin: Optional[str] = None
    regnumber: Optional[str] = None

    # Цены и торговля
    last_price: Optional[float] = None
    prevprice: Optional[float] = None
    prevwaprice: Optional[float] = None
    prevlegalcloseprice: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None

    # Валюта и шаг цены
    currencyid: Optional[str] = None
    minstep: Optional[float] = None
    decimals: Optional[int] = None
    settledate: Optional[date] = None

    # Лоты и объём выпуска
    lotsize: Optional[int] = None
    facevalue: Optional[float] = None
    issuesize: Optional[int] = None

    # Статус и листинг
    status: Optional[str] = None
    listlevel: Optional[int] = None
    sectype: Optional[str] = None

    # Классификация
    boardid: Optional[str] = None
    boardname: Optional[str] = None
    sectorid: Optional[str] = None
    marketcode: Optional[str] = None
    instrid: Optional[str] = None
