from decimal import Decimal
from typing import Optional

from pydantic import Field, computed_field, model_validator

from pymoex.utils.types import MoexDate, MoexDecimal, MoexInt

from .base import BaseInstrument


class Share(BaseInstrument):
    """
    Акция (или фонд) Московской биржи.

    Содержит:
    - идентификационные данные
    - текущие и исторические цены
    - параметры торгов
    - информацию о листинге и классификации
    """

    # --- Идентификация инструмента ---
    sec_id: str = Field(alias="SECID")
    """Идентификатор финансового инструмента"""

    board_id: Optional[str] = Field(None, alias="BOARDID")
    """Идентификатор режима торгов"""

    isin: Optional[str] = Field(None, alias="ISIN")
    """ISIN"""

    short_name: str = Field(alias="SHORTNAME")
    """Краткое наименование ценной бумаги"""

    name: Optional[str] = Field(None, alias="SECNAME")
    """Наименование финансового инструмента"""

    reg_number: Optional[str] = Field(None, alias="REGNUMBER")
    """Регистрационный номер"""

    status: Optional[str] = Field(None, alias="STATUS")
    """Статус"""

    list_level: MoexInt = Field(None, alias="LISTLEVEL")
    """Уровень листинга"""

    sec_type: Optional[str] = Field(None, alias="SECTYPE")
    """Тип ценной бумаги"""

    # --- Цены ---
    prev_price: MoexDecimal = Field(None, alias="PREVPRICE")
    """Предыдущая цена"""

    prev_weighted_price: MoexDecimal = Field(None, alias="PREVWAPRICE")
    """Предыдущая средневзвешенная цена"""

    prev_close_price: MoexDecimal = Field(None, alias="PREVLEGALCLOSEPRICE")
    """Официальная цена закрытия предыдущего дня"""

    close_price: MoexDecimal = Field(None, alias="CLOSEPRICE")
    """Цена закрытия"""

    last_price: MoexDecimal = Field(None, alias="LAST")
    """Последняя цена сделки"""

    open_price: MoexDecimal = Field(None, alias="OPEN")
    """Цена открытия"""

    high_price: MoexDecimal = Field(None, alias="HIGH")
    """Максимальная цена"""

    low_price: MoexDecimal = Field(None, alias="LOW")
    """Минимальная цена"""

    # --- Объемы торгов ---
    volume_today: MoexInt = Field(None, alias="VOLTODAY")
    """Объем торгов в штуках"""

    value_today: MoexDecimal = Field(None, alias="VALTODAY")
    """Объем торгов в валюте (руб)"""

    num_trades: MoexInt = Field(None, alias="NUMTRADES")
    """Количество сделок"""

    # --- Параметры ---
    currency_id: Optional[str] = Field(None, alias="CURRENCYID")
    """Валюта торгов"""

    min_step: MoexDecimal = Field(None, alias="MINSTEP")
    """Шаг цены"""

    decimals: MoexInt = Field(None, alias="DECIMALS")
    """Знаков после запятой"""

    settle_date: MoexDate = Field(None, alias="SETTLEDATE")
    """Дата расчёта"""

    lot_size: MoexInt = Field(None, alias="LOTSIZE")
    """Размер лота (бумаг)"""

    face_value: MoexDecimal = Field(None, alias="FACEVALUE")
    """Номинальная стоимость одной акции"""

    issue_size: MoexInt = Field(None, alias="ISSUESIZE")
    """Объём эмиссии"""

    # --- Служебная информация ---
    trading_status: Optional[str] = Field(None, alias="TRADINGSTATUS")
    """Состояние торговой сессии"""

    # --- Computed ---
    @computed_field
    @property
    def reference_price(self) -> Optional[Decimal]:
        """Базовая цена для сравнения."""
        return self.prev_weighted_price or self.prev_price

    @computed_field
    @property
    def effective_close(self) -> Optional[Decimal]:
        """Фактическая цена закрытия."""
        return self.close_price or self.prev_close_price

    # --- Validator ---
    @model_validator(mode="before")
    @classmethod
    def fix_missing_prices(cls, data: dict):
        """
        Если нет цены сделки (LAST), ищем цену закрытия или цену предыдущего дня.
        """
        if not data.get("LAST"):
            data["LAST"] = (
                data.get("CLOSEPRICE")
                or data.get("PREVPRICE")
                or data.get("PREVWAPRICE")
            )

        return data

    # --- Repr ---
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление акции."""
        parts = [self.sec_id]

        if self.short_name:
            parts.append(self.short_name)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        return f"<Share {' | '.join(parts)}>"


__all__ = ["Share"]
