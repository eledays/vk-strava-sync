from app.vk.bot import Bot
from app.utils.logging import log_message_handling

from logging import getLogger
import random

logger = getLogger(__name__)


def handle_help_message(bot: Bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    bot.send_message(
        user_id=user_id,
        message="Используй клавиатуру для управления. Если не отображает, отправь любое сообщение",
    )