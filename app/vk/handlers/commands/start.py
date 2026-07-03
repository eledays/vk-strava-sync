from app.utils.logging import log_message_handling
from app.vk.keyboards import get_navigate_keyboard

from logging import getLogger
from app.services.users import get_or_create_user_by_vk_id

logger = getLogger(__name__)


def handle_start_message(bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    user = get_or_create_user_by_vk_id(user_id)
    log_message_handling(logger, __name__, user_id, text)

    keyboard = get_navigate_keyboard()

    bot.send_message(
        user_id=user_id,
        message=(
            "Чтобы настроить синхронизацию выполни следующие шаги:\n\n"
            "1. Зарегистрируйся или войди в аккаунт на Strava: strava.com\n\n"
            "2. Установи в браузер расширение Cookie Editor: cookie-editor.com\n\n"
            "3. Скопируй JSON-cookies со strava.com с помощью Cookie Editor\n\n"
            "4. Выбери в меню \"Куки\" -> \"Установить куки\"\n\n"
            "5. Отправь скопированные куки"
        ),
        keyboard=keyboard,
    )