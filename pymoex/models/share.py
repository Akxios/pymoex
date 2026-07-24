from decimal import Decimal
from typing import override

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

    board_id: str | None = Field(default=None, alias="BOARDID")
    """Идентификатор режима торгов"""

    isin: str | None = Field(default=None, alias="ISIN")
    """ISIN"""

    short_name: str = Field(alias="SHORTNAME")
    """Краткое наименование ценной бумаги"""

    name: str | None = Field(default=None, alias="SECNAME")
    """Наименование финансового инструмента"""

    reg_number: str | None = Field(default=None, alias="REGNUMBER")
    """Регистрационный номер"""

    status: str | None = Field(default=None, alias="STATUS")
    """Статус"""

    list_level: MoexInt = Field(default=None, alias="LISTLEVEL")
    """Уровень листинга"""

    sec_type: str | None = Field(default=None, alias="SECTYPE")
    """Тип ценной бумаги"""

    # --- Цены ---
    prev_price: MoexDecimal = Field(default=None, alias="PREVPRICE")
    """Предыдущая цена"""

    prev_weighted_price: MoexDecimal = Field(default=None, alias="PREVWAPRICE")
    """Предыдущая средневзвешенная цена"""

    prev_close_price: MoexDecimal = Field(default=None, alias="PREVLEGALCLOSEPRICE")
    """Официальная цена закрытия предыдущего дня"""

    close_price: MoexDecimal = Field(default=None, alias="CLOSEPRICE")
    """Цена закрытия"""

    last_price: MoexDecimal = Field(default=None, alias="LAST")
    """Последняя цена сделки"""

    open_price: MoexDecimal = Field(default=None, alias="OPEN")
    """Цена открытия"""

    high_price: MoexDecimal = Field(default=None, alias="HIGH")
    """Максимальная цена"""

    low_price: MoexDecimal = Field(default=None, alias="LOW")
    """Минимальная цена"""

    # --- Объемы торгов ---
    volume_today: MoexInt = Field(default=None, alias="VOLTODAY")
    """Объем торгов в штуках"""

    value_today: MoexDecimal = Field(default=None, alias="VALTODAY")
    """Объем торгов в валюте (руб)"""

    num_trades: MoexInt = Field(default=None, alias="NUMTRADES")
    """Количество сделок"""

    # --- Параметры ---
    currency_id: str | None = Field(default=None, alias="CURRENCYID")
    """Валюта торгов"""

    min_step: MoexDecimal = Field(default=None, alias="MINSTEP")
    """Шаг цены"""

    decimals: MoexInt = Field(default=None, alias="DECIMALS")
    """Знаков после запятой"""

    settle_date: MoexDate = Field(default=None, alias="SETTLEDATE")
    """Дата расчёта"""

    lot_size: MoexInt = Field(default=None, alias="LOTSIZE")
    """Размер лота (бумаг)"""

    face_value: MoexDecimal = Field(default=None, alias="FACEVALUE")
    """Номинальная стоимость одной акции"""

    issue_size: MoexInt = Field(default=None, alias="ISSUESIZE")
    """Объём эмиссии"""

    # --- Служебная информация ---
    trading_status: str | None = Field(default=None, alias="TRADINGSTATUS")
    """Состояние торговой сессии"""

    # --- Computed ---
    @computed_field
    @property
    def reference_price(self) -> Decimal | None:
        """Базовая цена для сравнения."""
        return self.prev_weighted_price or self.prev_price

    @computed_field
    @property
    def effective_close(self) -> Decimal | None:
        """Фактическая цена закрытия."""
        return self.close_price or self.prev_close_price

    # --- Validator ---
    @model_validator(mode="before")
    @classmethod
    def fix_missing_prices(cls, data: dict[str, object]) -> dict[str, object]:
        """
        Если нет цены сделки (LAST), ищем цену закрытия или цену предыдущего дня.
        """
        if data.get("LAST") is None:
            data["LAST"] = next(
                (
                    value
                    for value in (
                        data.get("CLOSEPRICE"),
                        data.get("PREVPRICE"),
                        data.get("PREVWAPRICE"),
                    )
                    if value is not None
                ),
                None,
            )

        return data

    # --- Repr ---
    @override
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление акции."""
        parts = [self.sec_id]

        if self.short_name:
            parts.append(self.short_name)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        return f"<Share {' | '.join(parts)}>"

    # --- Str ---
    @override
    def __str__(self) -> str:
        return repr(self)


__all__ = ["Share"]
