from vk_api.vk_api import VkApiMethod

from app.vk.handlers.commands.help import handle_help_message
from app.vk.handlers.commands.unknown import handle_unknown_message

from logging import getLogger

logger = getLogger(__name__)


def handle_message(vk: VkApiMethod, message: dict):
    text = message["text"].lower()
    lower_text = text.lower().strip()

    if lower_text == 'помощь':
        handle_help_message(vk, message)
    else:
        handle_unknown_message(vk, message)


