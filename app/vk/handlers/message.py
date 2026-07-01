from app.vk.handlers.commands import (
    handle_help_message,
    handle_unknown_message,
    handle_cookie_message,
    handle_current_cookie_message,
    handle_set_cookie_message,
    handle_cookie_input
)
from app.vk.states import UserStateManager, CookieState

from logging import getLogger

logger = getLogger(__name__)


def handle_message(bot, message: dict):
    text = message["text"].strip()
    user_id = message["from_id"]

    handler = handle_unknown_message

    state = UserStateManager.get(user_id)
    if state == CookieState.AWAITING_COOKIES:
        handle_cookie_input(bot, message)
        return
    
    handlers = {
        'помощь': handle_help_message,
        'куки': handle_cookie_message,
        'текущие куки': handle_current_cookie_message,
        'установить куки': handle_set_cookie_message
    }
    
    handler = handlers.get(text.lower(), handle_unknown_message)
    handler(bot, message)


