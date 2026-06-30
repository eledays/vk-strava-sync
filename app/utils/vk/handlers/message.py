from app.vk.handlers.commands.help import handle_help_message

from logging import getLogger

logger = getLogger(__name__)


def handle_message(message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]
    lower_text = text.lower().strip()

    if lower_text == 'статус':
        handle_help_message(message)
    else:
        logger.info(f'Сообщение не обработано от {user_id}: {text[:20]}{"..." if len(text) > 20 else ""}')


