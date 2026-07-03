from app.utils.logging import log_message_handling
from app.vk.keyboards import (
    get_cookie_actions_keyboard,
    get_cancel_keyboard
)
from app.config import Config
from app.services.cookie import parse_cookies_from_string
from app.services.strava import StravaClient
from app.services.users import (
    get_or_create_user_by_vk_id,
    save_strava_cookies
)
from app.vk.states import UserStateManager, CookieState

from logging import getLogger
import json

logger = getLogger(__name__)


def handle_cookie_message(bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    keyboard = get_cookie_actions_keyboard()

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

    user = get_or_create_user_by_vk_id(user_id)
    cookies = parse_cookies_from_string(user.strava_cookies)
    
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
    UserStateManager.clear(user_id)

    if text == "отмена":
        bot.send_message(
            user_id=user_id,
            message="Отменено",
            keyboard=get_cookie_actions_keyboard(False)
        )
        return
    
    cookies = parse_cookies_from_string(text)

    if not cookies:
        bot.send_message(
            user_id=user_id,
            message="Неверный формат cookie",
            keyboard=get_cookie_actions_keyboard()
        )
        return

    bot.send_message(
        user_id=user_id,
        message="Пара секунд, провожу проверку cookie\n✅ Синтаксис в порядке\nПроверяю доступность strava"
    )

    user = get_or_create_user_by_vk_id(user_id)

    client = StravaClient(cookies)
    result, error_message = client.check_cookies()
    if result:
        bot.send_message(
            user_id=user_id,
            message="✅ Strava доступна",
            keyboard=get_cookie_actions_keyboard(True)
        )
        save_strava_cookies(user.id, json.dumps(cookies))
    else:
        bot.send_message(
            user_id=user_id,
            message=f"🚫 Strava недоступна. Cookie не сохранены. Ошибка: {error_message}",
            keyboard=get_cookie_actions_keyboard(False)
        )