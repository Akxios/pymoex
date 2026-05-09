from typing import override

from pydantic import Field

from pymoex.utils.types import MoexDate, MoexDecimal

from .base import BaseInstrument


class Coupon(BaseInstrument):
    """
    Модель купонной выплаты по облигации.

    Описывает параметры периодической процентной выплаты.
    Для облигаций с переменным купоном (флоатеров) будущие значения
    могут быть временно не определены.
    """

    sec_id: str = Field(alias="secid")
    """Идентификатор финансового инструмента"""

    isin: str | None = Field(default=None, alias="isin")
    """ISIN"""

    coupon_date: MoexDate = Field(alias="coupondate")
    """Дата фактической выплаты купона"""

    record_date: MoexDate | None = Field(default=None, alias="recorddate")
    """"
    Дата фиксации реестра владельцев. 
    Чтобы получить купон, бумагу нужно купить до этой даты
    """

    value: MoexDecimal | None = Field(default=None, alias="value")
    """
    Сумма выплаты в абсолютном выражении. 
    Для будущих выплат облигаций с плавающей ставкой (флоатеров) 
    может быть неизвестна (None)
    """

    value_prc: MoexDecimal | None = Field(default=None, alias="valueprc")
    """Размер купона в процентах годовых от номинала"""

    face_unit: str | None = Field(default=None, alias="faceunit")
    """Валюта номинала"""

    # --- Repr ---
    @override
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление купона."""
        val_str: str = (
            f"{self.value:.2f} {self.face_unit or ''}".strip()
            if self.value is not None
            else "Неизвестно"
        )
        return f"<Coupon | {self.sec_id} | date={self.coupon_date} | value={val_str}>"

    # --- Str ---
    @override
    def __str__(self) -> str:
        return repr(self)


class Amortization(BaseInstrument):
    """
    Модель выплаты части номинала (амортизации) по облигации.

    Описывает частичное погашение основного долга. Каждая такая выплата
    уменьшает непогашенный номинал бумаги, что влияет на последующие
    процентные расходы эмитента.
    """

    sec_id: str = Field(alias="secid")
    """Идентификатор финансового инструмента"""

    isin: str | None = Field(default=None, alias="isin")
    """ISIN"""

    amort_date: MoexDate = Field(alias="amortdate")
    """Дата выплаты части номинальной стоимости"""

    value: MoexDecimal | None = Field(default=None, alias="value")
    """Сумма погашаемой части номинала в абсолютном выражении"""

    value_prc: MoexDecimal | None = Field(default=None, alias="valueprc")
    """Процент от изначального номинала, который гасится в эту дату"""

    face_unit: str | None = Field(default=None, alias="faceunit")
    """Валюта номинала"""

    # --- Repr ---
    @override
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление купона и амортизации."""
        val_str = (
            f"{self.value:.2f} {self.face_unit or ''}".strip()
            if self.value is not None
            else "Неизвестно"
        )
        return (
            f"<Amortization | {self.sec_id} | date={self.amort_date} | value={val_str}>"
        )

    # --- Str ---
    @override
    def __str__(self) -> str:
        return repr(self)


__all__ = ["Coupon", "Amortization"]
