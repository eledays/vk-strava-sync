from vk_api.vk_api import VkApiMethod

from app.utils.logging import log_message_handling
from app.vk.keyboards.navigate import get_navigate_keyboard

from logging import getLogger

logger = getLogger(__name__)


def handle_unknown_message(vk, message):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    keyboard = get_navigate_keyboard()

    vk.messages.send(
        user_id=user_id,
        message="Привет",
        keyboard=keyboard,
        random_id=0
    )