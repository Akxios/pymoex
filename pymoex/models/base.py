from typing import ClassVar, override

from pydantic import BaseModel, ConfigDict


class BaseInstrument(BaseModel):
    """
    Базовая модель биржевого инструмента.

    Общие настройки:
    - принимает алиасы MOEX
    - игнорирует лишние поля
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    @override
    def __str__(self) -> str:
        return repr(self)
