from logging import getLogger

logger = getLogger(__name__)


class UserStateManager:
    """
    Простое FSM-хранилище в памяти.
    Расширяется без изменения кода — просто добавь новое состояние.
    """
    _states: dict[int, str | None] = {}

    @classmethod
    def get(cls, user_id: int) -> str | None:
        """Вернуть текущее состояние пользователя или None."""
        return cls._states.get(user_id)

    @classmethod
    def set(cls, user_id: int, state: str | None) -> None:
        """Установить состояние пользователя. state=None сбрасывает."""
        cls._states[user_id] = state
        logger.debug(f"User {user_id} state set to {state}")

    @classmethod
    def clear(cls, user_id: int) -> None:
        """Сбросить состояние пользователя в None."""
        cls._states[user_id] = None
        logger.debug(f"User {user_id} state cleared")