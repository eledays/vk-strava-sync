from app.vk.bot import Bot
from app.config import Config
from app.logger import setup_logging
from app.database import init_db


def main():
    setup_logging()
    init_db()

    bot = Bot(
        Config.VK_TOKEN,
        Config.VK_GROUP_ID
    )
    bot.run()


if __name__ == "__main__":
    main()
