from vk_api.vk_api import VkApiMethod

from app.utils.logging import log_message_handling
from app.vk.keyboards import get_cookie_actions_keyboard
from app.config import Config

from logging import getLogger

logger = getLogger(__name__)


def handle_cookie_message(vk, message):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    cookie_file_exists = Config.COOKIES_FILE.exists()
    keyboard = get_cookie_actions_keyboard(cookie_file_exists)

    vk.messages.send(
        user_id=user_id,
        message="Выбери действие",
        keyboard=keyboard,
        random_id=0
    )