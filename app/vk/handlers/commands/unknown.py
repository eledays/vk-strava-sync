from app.utils.logging import log_message_handling
from app.vk.keyboards import get_navigate_keyboard

from logging import getLogger
import random

logger = getLogger(__name__)


def handle_unknown_message(bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    keyboard = get_navigate_keyboard()

    bot.send_message(
        user_id=user_id,
        message="Привет",
        keyboard=keyboard,
    )