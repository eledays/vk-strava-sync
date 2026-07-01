from app.utils.logging import log_message_handling
from app.vk.keyboards import (
    get_cookie_actions_keyboard,
    get_cancel_keyboard
)
from app.config import Config
from app.services.cookie import parse_cookies
from app.vk.states import UserStateManager, CookieState

import random
from logging import getLogger

logger = getLogger(__name__)


def handle_cookie_message(bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    cookie_file_exists = Config.COOKIES_FILE.exists()
    keyboard = get_cookie_actions_keyboard(cookie_file_exists)

    bot.send_message(
        user_id=user_id,
        message="Выбери действие",
        keyboard=keyboard
    )


def handle_current_cookie_message(bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    keyboard = get_cookie_actions_keyboard(False)
    
    cookies = parse_cookies(Config.COOKIES_FILE)
    if not cookies:
        bot.send_message(
            user_id=user_id,
            message='Кук нет. Можно установить',
            keyboard=keyboard
        ) 
        return

    cookie_text = ''
    for i, cookie in enumerate(cookies, 1):
        cookie_text += f'{i}. {cookie.get("name")}: {cookie.get("domain")}\n'

    bot.send_message(
        user_id=user_id,
        message=cookie_text,
        keyboard=keyboard
    )


def handle_set_cookie_message(bot, message: dict):
    """Установка новых cookie."""
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)
    keyboard = get_cancel_keyboard()

    bot.send_message(
        user_id=user_id,
        message='Скопируй JSON-cookies с помощью Cookie-Editor с strava.com после успешной авторизации и отправь текстом',
        keyboard=keyboard
    )

    UserStateManager.set(user_id, CookieState.AWAITING_COOKIES)


def handle_cookie_input(bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    if text == "отмена":
        UserStateManager.clear(user_id)
        bot.send_message(
            user_id=user_id,
            message="Отменено",
            keyboard=get_cookie_actions_keyboard(False)
        )
        return

    print(text)
    UserStateManager.clear(user_id)