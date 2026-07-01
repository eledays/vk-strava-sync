import json
from pathlib import Path
from typing import Tuple


def parse_cookies_from_file(filepath: Path) -> list[dict]:
    """
    Получение списка cookie из файла.

    :param filepath: Path объект файла для парсинга
    :return: Список словарей cookie
    """
    if not filepath.exists():
        return []
    
    try:
        cookies = json.loads(filepath.read_text())
    except json.JSONDecodeError:
        return []
    
    if isinstance(cookies, dict):
        cookies = cookies["cookies"]
        
    return cookies


def parse_cookies_from_string(string: str) -> list[dict]:
    """
    Получение списка cookie из строки.

    :string str: Строка для парсинга
    :return: Список словарей cookie
    """
    if not string:
        return []
    
    try:
        cookies = json.loads(string)
    except json.JSONDecodeError:
        return []
    
    if isinstance(cookies, dict):
        cookies = cookies["cookies"]
        
    return cookies


def save_cookies_to_file(cookies: list[dict], filepath: Path) -> None:
    """
    Сохранение списка cookie в файл.

    :param cookies: Список словарей cookie
    :param filepath: Путь к файлу для сохранения
    """
    filepath.write_text(json.dumps(cookies))