import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from app.vk.handlers.message import handle_message

from logging import getLogger
from typing import Any, cast
import random

logger = getLogger(__name__)


class Bot:
    """
    Класс ВК-бота для обработки сообщений и событий из VK.
    """
    def __init__(self, token: str, vk_group_id: int) -> None:
        """
        Инициализация бота с использованием токена и ID группы VK, настройка сессии и Long Poll API для прослушивания событий.

        :param token: Токен доступа VK
        :param vk_group_id: ID группы VK
        """
        if token is None:
            raise ValueError('VK-токен не указан')
        
        if vk_group_id is None:
            raise ValueError('ID группы VK не указан')
        
        self.session = vk_api.VkApi(token=token)
        self.vk = self.session.get_api()
        self.longpoll = VkBotLongPoll(
            self.session, 
            group_id=vk_group_id
        )

    def run(self):
        logger.info("Bot started")

        for event in self.longpoll.listen():
            try:
                if event.type != VkBotEventType.MESSAGE_NEW:
                    continue

                if not event.from_user:  # type: ignore
                    continue

                msg = cast(dict[str, Any], event.obj.message)

                handle_message(self, msg)
            except Exception:
                logger.exception("Unhandled exception in event loop")

    def send_message(
            self, 
            user_id: int, 
            message: str, 
            keyboard: str | None = None, 
            **kwargs
        ):
        
        self.vk.messages.send(
            user_id=user_id,
            message=message,
            keyboard=keyboard,
            random_id=random.getrandbits(16),
            **kwargs
        )
