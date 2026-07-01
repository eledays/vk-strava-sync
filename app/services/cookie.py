import json
from pathlib import Path


def parse_cookies(filepath: Path) -> list:
    """
    Получение списка cookie из файла.

    :param filepath: Path объект файла для парсинг
    :return: Список словарей cookie
    """
    if not filepath.exists():
        return []
    
    cookies = json.loads(filepath.read_text())
    if isinstance(cookies, dict):
        cookies = cookies["cookies"]
    return cookies


def clean_cookie_filter(cookies: list) -> list:
    """
    Очистка cookie. Остаются только основные и безопасные поля, которыми можно делиться.

    :param cookies: Список словарей cookie
    :return: Отфильтрованный список словарей cookie  
    """
    KEYS = ['name', 'domain']

    result = []
    for cookie in cookies:
        result.append({k: cookie.get(k) for k in KEYS})

    return result