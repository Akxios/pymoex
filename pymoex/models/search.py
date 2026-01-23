from pydantic import BaseModel
from typing import Optional


class SearchResult(BaseModel):

    def __repr__(self) -> str:
        # Тип инструмента
        if self.group == "stock_bonds":
            kind = "Bond"
        elif self.group == "stock_shares":
            kind = "Share"
        elif self.group in {"options", "futures_options"}:
            kind = "Option"
        else:
            kind = "Instrument"

        parts = [self.secid]

        if self.shortname:
            parts.append(self.shortname)

        if self.emitent_title:
            parts.append(self.emitent_title)

        if self.is_traded is not None:
            parts.append("traded" if self.is_traded else "not traded")

        return f"<{kind} {' | '.join(parts)}>"

    def __str__(self) -> str:
        return self.__repr__()

    secid: str
    shortname: str
    name: str
    isin: Optional[str] = None
    regnumber: Optional[str] = None

    type: Optional[str] = None
    group: Optional[str] = None

    is_traded: Optional[bool] = None
    primary_boardid: Optional[str] = None
    marketprice_boardid: Optional[str] = None

    emitent_id: Optional[int] = None
    emitent_title: Optional[str] = None
    emitent_inn: Optional[str] = None


