from decimal import Decimal
from typing import Optional

from pydantic import Field, computed_field, model_validator

from pymoex.utils.types import MoexDate, MoexDecimal, MoexInt

from .base import BaseInstrument


class Bond(BaseInstrument):
    """
    Модель облигации Московской биржи.

    Содержит:
    - идентификационные данные бумаги
    - рыночные параметры (цена, доходность)
    - параметры купона
    - даты и сроки обращения
    - номинал и валюту
    - информацию о листинге и ликвидности
    - опционные события (оферты, выкуп)
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

    bond_type: Optional[str] = Field(None, alias="BONDTYPE")
    """Вид облигации"""

    bond_sub_type: Optional[str] = Field(None, alias="BONDSUBTYPE")
    """Подвид облигации"""

    # --- Параметры номинала ---
    face_value: MoexDecimal = Field(None, alias="FACEVALUE")
    """Непогашенный долг"""

    face_unit: Optional[str] = Field(None, alias="FACEUNIT")
    """Валюта номинала"""

    currency_id: Optional[str] = Field(None, alias="CURRENCYID")
    """Валюта, в которой проводятся расчеты по сделкам"""

    lot_size: MoexInt = Field(None, alias="LOTSIZE")
    """Размер лота"""

    lot_value: MoexDecimal = Field(None, alias="LOTVALUE")
    """Номинальная стоимость лота, в валюте номинала"""

    min_step: MoexDecimal = Field(None, alias="MINSTEP")
    """Мин. шаг цены"""

    issue_size_placed: MoexInt = Field(None, alias="ISSUESIZEPLACED")
    """Количество ценных бумаг в обращении"""

    # --- Купоны и доходность ---
    coupon_value: MoexDecimal = Field(None, alias="COUPONVALUE")
    """Сумма купона, в валюте номинала"""

    coupon_percent: MoexDecimal = Field(None, alias="COUPONPERCENT")
    """Ставка купона, %"""

    accruedint: MoexDecimal = Field(None, alias="ACCRUEDINT")
    """НКД на дату расчетов, в валюте расчетов"""

    next_coupon: MoexDate = Field(None, alias="NEXTCOUPON")
    """Дата окончания купона"""

    coupon_period: MoexInt = Field(None, alias="COUPONPERIOD")
    """Длительность купона"""

    # --- Календарь и цены ---
    mat_date: MoexDate = Field(None, alias="MATDATE")
    """Дата погашения"""

    buyback_date: MoexDate = Field(None, alias="BUYBACKDATE")
    """Дата, к кот.рассч.доходность"""

    buyback_price: MoexDecimal = Field(None, alias="BUYBACKPRICE")
    """Цена оферты"""

    offer_date: MoexDate = Field(None, alias="OFFERDATE")
    """Дата Оферты"""

    prev: MoexDecimal = Field(None, alias="PREV")
    """Цена последней сделки предыдущего торгового дня, % от номинала"""

    prev_price: MoexDecimal = Field(None, alias="PREVPRICE")
    """Цена последней сделки пред. дня, % к номиналу"""

    prev_weighted_price: MoexDecimal = Field(None, alias="PREVWAPRICE")
    """Средневзвешенная цена предыдущего дня, % к номиналу"""

    yield_dat_prev_wa_price: MoexDecimal = Field(None, alias="YIELDATPREVWAPRICE")
    """Доходность по оценке пред. дня"""

    # --- Цены (% от номинала) ---
    price_percent: MoexDecimal = Field(None, alias="LAST")
    """Цена последней сделки, %"""

    open_price: MoexDecimal = Field(None, alias="OPEN")
    """Цена первой сделки, % к номиналу"""

    close_price: MoexDecimal = Field(None, alias="CLOSE")
    """Цена последней сделки, %"""

    low_price: MoexDecimal = Field(None, alias="LOW")
    """Минимальная цена сделки, % к номиналу"""

    high_price: MoexDecimal = Field(None, alias="HIGH")
    """Максимальная цена сделки, % к номиналу"""

    weighted_price: MoexDecimal = Field(None, alias="WAPRICE")
    """Средневзвешенная цена, % к номиналу"""

    lclose_price: MoexDecimal = Field(None, alias="CLOSEPRICE")
    """Цена закрытия"""

    prev_close_price: MoexDecimal = Field(None, alias="PREVLEGALCLOSEPRICE")
    """Официальная цена закрытия предыдущего дня"""

    # --- Спрос и предложение ---
    bid: MoexDecimal = Field(None, alias="BID")
    """Цена спроса (котировка на покупку) на момент окончания торговой сессии, % от номинала"""

    offer: MoexDecimal = Field(None, alias="OFFER")
    """Цена предложения (котировка на продажу) на момент окончания торговой сессии, % от номинала"""

    spread: MoexDecimal = Field(None, alias="SPREAD")
    """Разница между лучшей котировкой на продажу и покупку (спред), % к номиналу"""

    bid_deptht: MoexInt = Field(None, alias="BIDDEPTHT")
    """Совокупный спрос"""

    offer_deptht: MoexInt = Field(None, alias="OFFERDEPTHT")
    """Общий объем котировок на продажу, лотов"""

    # --- Активность и объемы ---

    num_trades: MoexInt = Field(None, alias="NUMTRADES")
    """Количество заключенных сделок, штук"""

    volume_today: MoexInt = Field(None, alias="VOLTODAY")
    """Объем заключенных сделок в единицах ценных бумаг, штук"""

    value_today: MoexDecimal = Field(None, alias="VALTODAY")
    """Объем в валюте, в которой проводятся расчеты по сделкам"""

    qty: MoexInt = Field(None, alias="QTY")
    """Объем последней сделки, лотов"""

    value: MoexDecimal = Field(None, alias="VALUE")
    """Объем последней сделки, руб."""

    # --- Расчетные показатели ---

    last_yield: MoexDecimal = Field(None, alias="YIELD")
    """Доходность по последней сделке"""

    effective_yield: MoexDecimal = Field(None, alias="EFFECTIVEYIELD")
    """Эффективная доходность"""

    yield_at_weighted_price: MoexDecimal = Field(None, alias="YIELDATWAPRICE")
    """Доходность по средневзвешенной цене, % годовых"""

    duration: MoexInt = Field(None, alias="DURATION")
    """Дюрация, дней"""

    last_change: MoexInt = Field(None, alias="LASTCHANGE")
    """Изменение цены последней сделки к цене последней сделки предыдущего торгового дня"""

    # --- Служебная информация ---
    trading_status: Optional[str] = Field(None, alias="TRADINGSTATUS")
    """Состояние торговой сессии"""

    # --- Computed ---
    @computed_field
    @property
    def last_price(self) -> Optional[Decimal]:
        """Последняя чистая цена в валюте (Nominal * Price%)."""
        if self.price_percent is None or self.face_value is None:
            return None

        return self.face_value * self.price_percent / Decimal(100)

    @computed_field
    @property
    def last_dirty_price(self) -> Optional[Decimal]:
        """Грязная цена (Clean Price + НКД)."""
        clean = self.last_price

        if clean is None:
            return None

        return clean + (self.accruedint or Decimal(0))

    # --- Validator ---
    @model_validator(mode="before")
    @classmethod
    def fix_missing_prices(cls, data: dict):
        """
        Если нет цены сделки (LAST), ищем цену закрытия или предыдущего дня.
        """

        if not data.get("LAST"):
            data["LAST"] = data.get("PREV") or data.get("PREVWAPRICE")

        if not data.get("EFFECTIVEYIELD"):
            data["EFFECTIVEYIELD"] = data.get("YIELD")

        return data

    # --- Repr ---
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление облигации."""
        parts = [self.sec_id]

        if self.short_name:
            parts.append(self.short_name)

        if self.last_price is not None:
            parts.append(f"price={self.last_price}")

        if self.effective_yield is not None:
            parts.append(f"yield={self.effective_yield:.2f}%")

        return f"<Bond {' | '.join(parts)}>"


__all__ = ["Bond"]
