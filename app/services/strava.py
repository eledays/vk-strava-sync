from app.config import Config

import json
import re
from pathlib import Path

import httpx


class StravaUploader:
    def __init__(self):
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

        cookies = json.loads(Path(Config.COOKIES_FILE).read_text())

        if isinstance(cookies, dict):
            cookies = cookies["cookies"]

        for cookie in cookies:
            self.client.cookies.set(
                name=cookie["name"],
                value=cookie["value"],
                domain=cookie["domain"],
                path=cookie["path"],
            )

    def _csrf(self) -> str:
        r = self.client.get(f"{Config.STRAVA_BASE_URL}/upload/select")
        r.raise_for_status()

        m = re.search(
            r'name="csrf-token"\s+content="([^"]+)"',
            r.text,
        )

        if not m:
            raise RuntimeError("CSRF token not found")

        return m.group(1)

    def upload(self, gpx_path: str):
        token = self._csrf()

        with open(gpx_path, "rb") as f:
            files = {
                "files[]": (
                    Path(gpx_path).name,
                    f,
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

