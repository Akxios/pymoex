from pydantic import BaseModel
from typing import Optional


class Share(BaseModel):
    secid: str
    shortname: str
    last_price: Optional[float] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
