from vk_api.vk_api import VkApiMethod

from app.utils.logging import log_message_handling
from app.vk.keyboards.navigate import get_navigate_keyboard

from logging import getLogger

logger = getLogger(__name__)


def handle_help_message(vk, message):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    vk.messages.send(
        user_id=user_id,
        message="Используй клавиатуру для управления. Если не отображает, отправь любое сообщение",
        random_id=0
    )