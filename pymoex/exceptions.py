class MoexError(Exception):
    pass
    """Базовое исключение для всех ошибок SDK pymoex."""


class InstrumentNotFoundError(MoexError):
    pass
    """Акция или облигация не найдена на Московской бирже."""


class MoexAPIError(MoexError):
    pass
    """Базовое исключение для ошибок ISS API."""


class MoexNetworkError(MoexError):
    pass
    """Базовое исключение для сетевых и HTTP ошибок."""


class MoexHTTPError(MoexNetworkError):
    """Базовое исключение для HTTP статусов 4xx/5xx."""


class MoexBadRequestError(MoexHTTPError):
    """Некорректный запрос к API (HTTP 400)."""


class MoexAuthError(MoexHTTPError):
    """Ошибка авторизации/аутентификации (HTTP 401/403)."""


class MoexNotFoundError(MoexHTTPError):
    """Ресурс не найден (HTTP 404)."""


class MoexRateLimitError(MoexHTTPError):
    """Превышен лимит запросов (HTTP 429)."""


class MoexServerError(MoexHTTPError):
    """Ошибка на стороне MOEX API (HTTP 5xx)."""


class MoexTimeoutError(MoexNetworkError):
    """Таймаут сетевого запроса к MOEX API."""


class MoexResponseParseError(MoexAPIError):
    """Ошибка декодирования JSON или неожиданный формат ответа."""
