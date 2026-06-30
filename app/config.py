from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()


class Config:
    VK_TOKEN = os.environ["VK_TOKEN"]
    VK_GROUP_ID = int(os.environ["VK_GROUP_ID"])
    STRAVA_BASE_URL = os.environ.get(
        "STRAVA_BASE_URL", "https://www.strava.com")

    PROXY_URL = os.environ.get("PROXY_URL", None)

    BASE_DIR = Path(__file__).parent.parent.resolve()
    COOKIES_FILE = BASE_DIR / "cookies.json"

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"