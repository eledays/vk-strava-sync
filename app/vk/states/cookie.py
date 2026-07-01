from enum import Enum


class CookieState(str, Enum):
    """Состояния для сценария работы с куки."""
    AWAITING_COOKIES = "AWAITING_COOKIES"