from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Config:
    VK_TOKEN = os.environ["VK_TOKEN"]
    STRAVA_BASE_URL = os.environ.get("STRAVA_BASE_URL", "https://www.strava.com")

    PROXY_URL = os.environ.get("PROXY_URL", None)

    BASE_DIR = Path(__file__).parent.resolve()
    COOKIES_FILE = BASE_DIR / "cookies.json"