from pydantic import BaseModel, ConfigDict


class BaseInstrument(BaseModel):
    """
    Базовая модель биржевого инструмента.

    Общие настройки:
    - принимает алиасы MOEX
    - игнорирует лишние поля
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    def __str__(self) -> str:
        return self.__repr__()
