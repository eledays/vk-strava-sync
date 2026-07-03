from app.utils.logging import log_message_handling
from app.services.strava import StravaClient
from app.services.users import get_or_create_user_by_vk_id
from app.services.cookie import parse_cookies_from_string

from logging import getLogger

logger = getLogger(__name__)


def handle_status_message(bot, message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    log_message_handling(logger, __name__, user_id, text)
    user = get_or_create_user_by_vk_id(user_id)

    sent_msg_id = bot.send_message(
        user_id=user_id,
        message="Проверяю доступность strava...",
    )

    client = StravaClient(parse_cookies_from_string(user.strava_cookies))
    is_available, error = client.check_access()

    has_cookies = user.strava_cookies is not None
        
    bot.delete_message(
        peer_id=message["peer_id"],
        message_id=sent_msg_id
    )

    if not is_available and has_cookies:
        bot.send_message(
            user_id=user_id,
            message=f"🚫 Strava недоступна: {error}\n✅ Cookies установлены\n🚫 Проверить валидность cookies не удалось",
        )
    elif not is_available and not has_cookies:
        bot.send_message(
            user_id=user_id,
            message=f"🚫 Strava недоступна: {error}\n🚫 Cookies не установлены",
        )
    elif is_available and not has_cookies:
        bot.send_message(
            user_id=user_id,
            message=f"✅ Strava доступна\n🚫 Cookies не установлены",
        )
    else:
        sent_msg_id = bot.send_message(
            user_id=user_id,
            message=f"✅ Strava доступна\n✅ Cookies установлены\nПроверяю валидность cookies...",
        )

        is_valid, error = client.check_cookies()
        
        bot.delete_message(
            peer_id=message["peer_id"],
            message_id=sent_msg_id
        )

        if not is_valid:
            bot.send_message(
                user_id=user_id,
                message=f"✅ Strava доступна\n✅ Cookies установлены\n🚫 Cookies не валидны",
            )
        else:
            bot.send_message(
                user_id=user_id,
                message=f"✅ Strava доступна\n✅ Cookies установлены\n✅ Cookies валидны",
            )


