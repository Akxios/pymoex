from typing import override

from pydantic import BaseModel, ConfigDict


class BaseInstrument(BaseModel):
    """
    Базовая модель биржевого инструмента.

    Общие настройки:
    - принимает алиасы MOEX
    - игнорирует лишние поля
    """

    model_config: ConfigDict = ConfigDict(  # pyright: ignore[reportIncompatibleVariableOverride]
        populate_by_name=True,
        extra="ignore",
    )

    @override
    def __str__(self) -> str:
        return repr(self)
