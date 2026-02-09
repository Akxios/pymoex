class MoexError(Exception):
    """
    Базовое исключение для всех ошибок SDK pymoex.
    От него наследуются все остальные ошибки.
    """

    pass


class InstrumentNotFoundError(MoexError):
    """
    Акция или облигация не найдена на Московской бирже.
    """

    pass


class MoexAPIError(MoexError):
    """
    Ошибка ответа ISS API (500, битый JSON, неожиданный формат).
    """

    pass


class MoexNetworkError(MoexError):
    """Ошибки сети или HTTP статусы 4xx/5xx"""

    pass
