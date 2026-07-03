from app.utils.logging import log_message_handling
from app.services.strava import StravaClient

from logging import getLogger

logger = getLogger(__name__)


def handle_status_message(bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)

    bot.send_message(
        user_id=user_id,
        message="Проверяю доступность strava",
    )

    client = StravaClient()
    is_available, error = client.check_access()

    if is_available:
        bot.send_message(
            user_id=user_id,
            message="✅ Strava доступна",
        )
    else:
        bot.send_message(
            user_id=user_id,
            message=f"🚫 Strava недоступна: {error}",
        )


