from pydantic import BaseModel
from typing import Optional
from datetime import date


class Bond(BaseModel):
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

    couponvalue: Optional[float] = None
    couponpercent: Optional[float] = None
    accruedint: Optional[float] = None
    nextcoupon: Optional[date] = None

    # Срок и выплаты
    matdate: Optional[date] = None
    couponperiod: Optional[int] = None
    dateyieldfromissuer: Optional[date] = None

    # Номинал и лоты
    facevalue: Optional[float] = None
    lotsize: Optional[int] = None
    lotvalue: Optional[float] = None
    faceunit: Optional[str] = None
    currencyid: Optional[str] = None

    # Ликвидность и надёжность
    issuesizeplaced: Optional[int] = None
    listlevel: Optional[int] = None
    status: Optional[str] = None
    sectype: Optional[str] = None

    # Опции и особенности
    offerdate: Optional[date] = None
    calloptiondate: Optional[date] = None
    putoptiondate: Optional[date] = None
    buybackdate: Optional[date] = None
    buybackprice: Optional[float] = None

    # Классификация
    bondtype: Optional[str] = None
    bondsubtype: Optional[str] = None
    sectorid: Optional[str] = None
