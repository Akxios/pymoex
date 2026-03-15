from typing import Optional

from pydantic import Field, model_validator

from pymoex.utils.types import MoexDecimal, MoexInt

from .base import BaseInstrument


class Currency(BaseInstrument):
    """
    Модель валютной пары Московской биржи.
    """

    # --- Идентификация инструмента ---
    sec_id: str = Field(alias="SECID")
    """Идентификатор финансового инструмента"""

    board_id: Optional[str] = Field(None, alias="BOARDID")
    """Код площадки"""

    short_name: str = Field(alias="SHORTNAME")
    """Краткое наименование ценной бумаги"""

    name: Optional[str] = Field(None, alias="SECNAME")
    """Наименование финансового инструмента"""

    status: Optional[str] = Field(None, alias="STATUS")
    """Статус инструмента"""

    # --- Цены ---
    last_price: MoexDecimal = Field(None, alias="LAST")
    """Цена последней сделки"""

    prev_price: MoexDecimal = Field(None, alias="PREVPRICE")
    """Предыдущая цена"""

    open_price: MoexDecimal = Field(None, alias="OPEN")
    """Цена открытия"""

    high_price: MoexDecimal = Field(None, alias="HIGH")
    """Максимальная цена"""

    low_price: MoexDecimal = Field(None, alias="LOW")
    """Минимальная цена"""

    close_price: MoexDecimal = Field(None, alias="CLOSEPRICE")
    """Цена закрытия"""

    # --- Объемы торгов ---
    volume_today: MoexInt = Field(None, alias="VOLTODAY")
    """Объем торгов в штуках"""

    value_today: MoexDecimal = Field(None, alias="VALTODAY")
    """Объем торгов в валюте"""

    num_trades: MoexInt = Field(None, alias="NUMTRADES")
    """Количество сделок"""

    # --- Параметры ---
    lot_size: MoexInt = Field(None, alias="LOTSIZE")
    """Размер лота (обычно 1000)"""

    face_value: MoexDecimal = Field(None, alias="FACEVALUE")
    """Номинал"""

    min_step: MoexDecimal = Field(None, alias="MINSTEP")
    """Шаг цены"""

    # --- Validator ---
    @model_validator(mode="before")
    @classmethod
    def fix_missing_prices(cls, data: dict):
        """
        Если нет цены сделки (LAST), ищем цену закрытия, средневзвешенную
        или цену предыдущего дня.
        """
        if not data.get("LAST"):
            data["LAST"] = (
                data.get("CLOSEPRICE") or data.get("WAPRICE") or data.get("PREVPRICE")
            )

        return data

    # --- Repr ---
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление валюты."""
        parts = [self.sec_id]

        if self.short_name:
            parts.append(self.short_name)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        return f"<Currency {' | '.join(parts)}>"


__all__ = ["Currency"]
