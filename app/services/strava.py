from app.config import Config
from app.services.cookie import parse_cookies_from_file

import json
import re
from pathlib import Path
from logging import getLogger

import httpx

logger = getLogger(__name__)


class StravaClient:
    def __init__(self, cookies: list[dict]):
        self.client = httpx.Client(
            proxy=Config.PROXY_URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/146.0.0.0 Safari/537.36"
                ),
                "X-Requested-With": "XMLHttpRequest",
            },
            follow_redirects=True,
            timeout=60,
        )

        for cookie in cookies:
            name = cookie.get("name", "")
            value = cookie.get("value", "")
            domain = cookie.get("domain", "")
            path = cookie.get("path", "")
            if not all([name, value, domain]):
                logger.warning("Skipping invalid cookie entry: %s", cookie)
                continue
            self.client.cookies.set(name=name, value=value, domain=domain, path=path)

    def check_cookies(self) -> bool:
        r = self.client.get(f"{Config.STRAVA_BASE_URL}/upload/select")
        return r.status_code == 200

    def _csrf(self) -> str:
        resp = self.client.get(f"{Config.STRAVA_BASE_URL}/upload/select")
        resp.raise_for_status()

        m = re.search(
            r'name="csrf-token"\s+content="([^"]+)"',
            resp.text,
        )

        if not m:
            raise RuntimeError("CSRF token not found")

        return m.group(1)

    def upload(self, gpx_path: str):
        token = self._csrf()

        with open(gpx_path, "rb") as file:
            files = {
                "files[]": (
                    Path(gpx_path).name,
                    file,
                    "application/gpx+xml",
                )
            }

            data = {
                "_method": "post",
                "authenticity_token": token,
            }

            headers = {
                "X-CSRF-Token": token,
                "Accept": "text/plain, */*; q=0.01",
                "Origin": Config.STRAVA_BASE_URL,
                "Referer": f"{Config.STRAVA_BASE_URL}/upload/select",
            }

            r = self.client.post(
                f"{Config.STRAVA_BASE_URL}/upload/files",
                headers=headers,
                data=data,
                files=files,
            )

        r.raise_for_status()

        return r.json()

