from typing import Optional

from pydantic import Field

from pymoex.utils.types import MoexDate, MoexDecimal

from .base import BaseInstrument


class Coupon(BaseInstrument):
    """Модель купонной выплаты по облигации."""

    sec_id: str = Field(alias="secid")
    """Идентификатор финансового инструмента"""

    isin: Optional[str] = Field(None, alias="isin")
    """ISIN"""

    coupon_date: MoexDate = Field(alias="coupondate")
    """Дата фактической выплаты купона"""

    record_date: Optional[MoexDate] = Field(None, alias="recorddate")
    """"Дата фиксации реестра владельцев. Чтобы получить купон, бумагу нужно купить до этой даты"""

    value: Optional[MoexDecimal] = Field(None, alias="value")
    """Сумма выплаты в абсолютном выражении. Для будущих выплат облигаций с плавающей ставкой (флоатеров) может быть неизвестна (None)"""

    value_prc: Optional[MoexDecimal] = Field(None, alias="valueprc")
    """Размер купона в процентах годовых от номинала"""

    face_unit: Optional[str] = Field(None, alias="faceunit")
    """Валюта номинала"""

    def __repr__(self) -> str:
        val_str = (
            f"{self.value} {self.face_unit or ''}".strip()
            if self.value is not None
            else "Неизвестно"
        )
        return f"<Coupon | {self.sec_id} | date={self.coupon_date} | value={val_str}>"


class Amortization(BaseInstrument):
    """Модель выплаты части номинала (амортизации) по облигации."""

    sec_id: str = Field(alias="secid")
    """Идентификатор финансового инструмента"""

    isin: Optional[str] = Field(None, alias="isin")
    """ISIN"""

    amort_date: MoexDate = Field(alias="amortdate")
    """Дата выплаты части номинальной стоимости"""

    value: Optional[MoexDecimal] = Field(None, alias="value")
    """Сумма погашаемой части номинала в абсолютном выражении"""

    value_prc: Optional[MoexDecimal] = Field(None, alias="valueprc")
    """Процент от изначального номинала, который гасится в эту дату"""

    face_unit: Optional[str] = Field(None, alias="faceunit")
    """Валюта номинала"""

    # --- Repr ---
    def __repr__(self) -> str:
        """Короткое человекочитаемое представление купона и амортизации."""
        val_str = (
            f"{self.value} {self.face_unit or ''}".strip()
            if self.value is not None
            else "Неизвестно"
        )
        return (
            f"<Amortization | {self.sec_id} | date={self.amort_date} | value={val_str}>"
        )


__all__ = ["Coupon", "Amortization"]
