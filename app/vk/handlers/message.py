from app.vk.handlers.commands import (
    handle_help_message,
    handle_unknown_message,
    handle_cookie_message,
    handle_current_cookie_message,
    handle_set_cookie_message,
    handle_cookie_input,
    handle_status_message,
    handle_start_message
)
from app.vk.states import UserStateManager, CookieState

from logging import getLogger

logger = getLogger(__name__)


def handle_message(bot, message: dict):
    attachments = message.get("attachments", [])

    if any(attachment["type"] == "doc" for attachment in attachments):
        handle_document_message(bot, message)
    elif message.get("text"):
        handle_text_message(bot, message)
    else:
        logger.warning("Received message with no text or document attachment")


def handle_text_message(bot, message: dict):
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
        'установить куки': handle_set_cookie_message,
        'статус': handle_status_message,
        'начать': handle_start_message,
        'начало работы': handle_start_message
    }

    handler = handlers.get(text.lower(), handle_unknown_message)
    handler(bot, message)


def handle_document_message(bot, message: dict):
    docs = [attachment["doc"] for attachment in message.get(
        "attachments", []) if attachment["type"] == "doc"]

    if len(docs) > 1:
        bot.send_message(
            user_id=message["from_id"],
            message="Получил несколько файлов, смогу обработать только первый"
        )

    doc = docs[0]
    name: str = doc["title"]
    file_extension = name.split(".")[-1].lower()

    if file_extension == "fit":
        bot.send_message(
            user_id=message["from_id"],
            message="О, это .fit файл, я такой знаю"
        )
    else:
        bot.send_message(
            user_id=message["from_id"],
            message="С такими файлами я работать не умею. Пришли .fit"
        )
