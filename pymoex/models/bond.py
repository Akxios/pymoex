from pydantic import BaseModel
from typing import Optional


class Bond(BaseModel):
    secid: str
    shortname: str
    last_price: Optional[float] = None
    yield_percent: Optional[float] = None
