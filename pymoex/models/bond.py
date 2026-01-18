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
    regnumber: Optional[str] = None

    # Цена и доходность
    last_price: Optional[float] = None
    prevwaprice: Optional[float] = None
    prevprice: Optional[float] = None
    prevlegalcloseprice: Optional[float] = None
    yieldatprevwaprice: Optional[float] = None
    yield_percent: Optional[float] = None

    # Купоны
    couponvalue: Optional[float] = None
    couponpercent: Optional[float] = None
    accruedint: Optional[float] = None
    nextcoupon: Optional[date] = None

    # Срок обращения
    matdate: Optional[date] = None
    couponperiod: Optional[int] = None
    dateyieldfromissuer: Optional[date] = None

    # Номинал и лоты
    facevalue: Optional[float] = None
    lotsize: Optional[int] = None
    lotvalue: Optional[float] = None
    faceunit: Optional[str] = None
    currencyid: Optional[str] = None

    # Ликвидность и листинг
    issuesizeplaced: Optional[int] = None
    listlevel: Optional[int] = None
    status: Optional[str] = None
    sectype: Optional[str] = None

    # Опции (оферты, выкуп)
    offerdate: Optional[date] = None
    calloptiondate: Optional[date] = None
    putoptiondate: Optional[date] = None
    buybackdate: Optional[date] = None
    buybackprice: Optional[float] = None

    # Классификация
    bondtype: Optional[str] = None
    bondsubtype: Optional[str] = None
    sectorid: Optional[str] = None
