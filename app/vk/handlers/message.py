from app.vk.bot import Bot
from app.vk.handlers.commands import (
    handle_help_message,
    handle_unknown_message,
    handle_cookie_message,
    handle_current_cookie_message
)

from logging import getLogger

logger = getLogger(__name__)


def handle_message(bot: Bot, message: dict):
    text = message["text"].strip()

    handlers = {
        'помощь': handle_help_message,
        'куки': handle_cookie_message,
        'текущие куки': handle_current_cookie_message
    }
    
    handler = handlers.get(text.lower(), handle_unknown_message)
    handler(bot, message)


