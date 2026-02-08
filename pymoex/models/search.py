from typing import Optional

from pydantic import Field

from .base import BaseInstrument


class Search(BaseInstrument):
    """
    Модель результата поиска
    """

    # --- Идентификаторы ---
    sec_id: str = Field(alias="secid", description="Тикер")
    short_name: str = Field(alias="shortname", description="Краткое название")
    name: Optional[str] = Field(None, alias="name", description="Полное название")
    isin: Optional[str] = Field(None, alias="isin")
    reg_number: Optional[str] = Field(
        None, alias="regnumber", description="Рег. номер (для акций/облигаций)"
    )

    # --- Классификация ---
    type: Optional[str] = Field(None, alias="type")
    group: Optional[str] = Field(None, alias="group")

    # --- Торговые данные ---
    is_traded: Optional[bool] = Field(False, alias="is_traded")
    primary_boardid: Optional[str] = Field(
        None, alias="primary_boardid", description="Главный режим торгов"
    )
    marketprice_boardid: Optional[str] = Field(None, alias="marketprice_boardid")

    # --- Эмитент (Компания) ---
    emitent_id: Optional[int] = Field(None, alias="emitent_id")
    emitent_title: Optional[str] = Field(
        None, alias="emitent_title", description="Юридическое название эмитента"
    )
    emitent_inn: Optional[str] = Field(None, alias="emitent_inn")
    emitent_okpo: Optional[str] = Field(None, alias="emitent_okpo")

    def __repr__(self) -> str:
        status = "traded" if self.is_traded else "hidden"
        return f"<Search {self.sec_id} | {self.short_name} | {self.group} | {status}>"


__all__ = ["Search"]
