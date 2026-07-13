from app.config import Config
from app.services.cookie import parse_cookies_from_file

import http.cookiejar
import json
import re
from pathlib import Path
from logging import getLogger
from typing import Tuple

import httpx

logger = getLogger(__name__)


class StravaClient:
    def __init__(self, cookies: list[dict] | None = None):
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

        if cookies is not None:
            for cookie in cookies:
                name = cookie.get("name", "")
                value = cookie.get("value", "")
                domain = cookie.get("domain", "")
                path = cookie.get("path", "/")

                if not name or domain is None:
                    logger.warning("Invalid cookie entry: %s", cookie)
                    continue

                expires = None
                if cookie.get("expirationDate"):
                    expires = int(cookie["expirationDate"])

                c = http.cookiejar.Cookie(
                    version=0,
                    name=name,
                    value=value,
                    port=None,
                    port_specified=False,
                    domain=domain,
                    domain_specified=bool(domain),
                    domain_initial_dot=domain.startswith("."),
                    path=path,
                    path_specified=True,
                    secure=cookie.get("secure", False),
                    expires=expires,
                    discard=expires is None,
                    comment=None,
                    comment_url=None,
                    rest={"HttpOnly": cookie.get("httpOnly", False)},
                    rfc2109=False,
                )

                self.client.cookies.jar.set_cookie(c)

    def check_cookies(self) -> Tuple[bool, str | None]:
        """
        Проверка cookies запросом strava

        :return: True/False - валидность cookies, сообщение об ошибке
        """
        url = f"{Config.STRAVA_BASE_URL}/upload/select"

        if Config.SKIP_STRAVA_REQUESTS:
            logger.warning("Skipping Strava requests")
            return True, None

        try:
            response = self.client.get(url, timeout=30)
        except httpx.TimeoutException:
            logger.exception("Error while checking cookies")
            return False, "Таймаут"
        except httpx.HTTPError as e:
            logger.exception("Error while checking cookies")
            return False, f"{e}"
        except Exception:
            logger.exception("Error while checking cookies")
            return False, "Неизвестная ошибка"
        
        if response.status_code != 200:
            logger.error("Error while checking cookies, status code: %s", response.status_code)
            return False, f"код {response.status_code}"
        
        logger.info("Successfully checked cookies")
        return True, None
    
    def check_access(self) -> Tuple[bool, str | None]:
        url = Config.STRAVA_BASE_URL

        if Config.SKIP_STRAVA_REQUESTS:
            logger.warning("Skipping Strava requests")
            return True, None

        try:
            response = self.client.get(url, timeout=30)
        except httpx.TimeoutException:
            logger.exception("Error while checking access to strava")
            return False, "Таймаут"
        except httpx.HTTPError as e:
            logger.exception("Error while checking access to strava")
            return False, f"{e}"
        except Exception:
            logger.exception("Error while checking access to strava")
            return False, "Неизвестная ошибка"
        
        if response.status_code != 200:
            return False, f"код {response.status_code}"
        
        return True, None

    def _csrf(self) -> str:
        if Config.SKIP_STRAVA_REQUESTS:
            logger.warning("Skipping Strava requests")
            return ""
        
        resp = self.client.get(f"{Config.STRAVA_BASE_URL}/upload/select")
        resp.raise_for_status()

        m = re.search(
            r'name="csrf-token"\s+content="([^"]+)"',
            resp.text,
        )

        if not m:
            raise RuntimeError("CSRF token not found")

        return m.group(1)

    def upload(self, file_path: str):
        """
        Загрузка файла активности в Strava.

        Поддерживает .gpx (application/gpx+xml) и .fit (application/octet-stream).

        :param file_path: Путь к файлу для загрузки
        :return: JSON-ответ от Strava
        """
        token = self._csrf()

        if Config.SKIP_STRAVA_REQUESTS:
            logger.warning("Skipping Strava requests")
            return {}

        ext = Path(file_path).suffix.lower()
        mime_type = "application/gpx+xml" if ext == ".gpx" else "application/octet-stream"

        with open(file_path, "rb") as file:
            files = {
                "files[]": (
                    Path(file_path).name,
                    file,
                    mime_type,
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

