from app.services.strava import StravaClient
from app.services.cookie import parse_cookies_from_string
from app.services.users import get_or_create_user_by_vk_id

import tempfile
from pathlib import Path
from logging import getLogger
import requests

logger = getLogger(__name__)


def handle_fit_file(bot, message: dict, doc: dict):
    user_id = message["from_id"]
    user = get_or_create_user_by_vk_id(user_id)
    filename = doc.get("title", "activity.fit")

    if not user.strava_cookies:
        bot.send_message(
            user_id=user_id,
            message=(
                "🚫 Куки Strava не установлены"
            ),
        )
        return

    cookies = parse_cookies_from_string(user.strava_cookies)
    if not cookies:
        bot.send_message(
            user_id=user_id,
            message="🚫 Сохранённые куки Strava не валидны. Попробуй установить их заново",
        )
        return

    file_url = doc.get("url")
    if not file_url:
        bot.send_message(
            user_id=user_id,
            message="🚫 Не удалось получить ссылку на файл. Попробуй ещё раз",
        )
        return

    bot.send_message(
        user_id=user_id,
        message="Загружаю...",
    )

    print(file_url)

    for i in range(5):
        try:
            response = requests.get(file_url, timeout=120, allow_redirects=True)
            response.raise_for_status()
            break
        except Exception:
            logger.exception("Failed to download file from VK. Attempt %d/5", i + 1)
    else:
        bot.send_message(
            user_id=user_id,
            message="🚫 Не удалось скачать файл. Попробуй ещё раз",
        )
        return


    tmp_dir = Path(tempfile.gettempdir()) / "vk-strava-sync"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_file = tmp_dir / filename

    try:
        tmp_file.write_bytes(response.content)
    except Exception:
        logger.exception("Failed to save temporary file")
        bot.send_message(
            user_id=user_id,
            message="🚫 Ошибка при сохранении файла. Попробуй ещё раз",
        )
        return

    try:
        client = StravaClient(cookies=cookies)
        result = client.upload(str(tmp_file))
    except Exception:
        logger.exception("Failed to upload file to Strava")
        bot.send_message(
            user_id=user_id,
            message="🚫 Не удалось загрузить файл в Strava. Проверь куки и попробуй ещё раз",
        )
        return
    finally:
        try:
            tmp_file.unlink(missing_ok=True)
        except Exception:
            logger.warning("Failed to remove temporary file: %s", tmp_file)

    logger.info("Strava upload response: %s", result)

    item: dict = result[0]
    if item.get("error") is None:
        activity_id = item.get("id")
        msg = (
            "✅ Файл успешно загружен в Strava!\n"
            "https://www.strava.com/athlete/training"
        )
        bot.send_message(user_id=user_id, message=msg)
    else:
        bot.send_message(
            user_id=user_id,
            message="🚫 Strava вернула неожиданный ответ",
        )