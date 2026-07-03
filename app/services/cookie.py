import json
from pathlib import Path
from typing import Optional


def parse_cookies_from_file(filepath: Path) -> list[dict]:
    """
    Получение списка cookie из файла.

    :param filepath: Path объект файла для парсинга
    :return: Список словарей cookie
    """
    if not filepath.exists():
        return []
    
    try:
        data = json.loads(filepath.read_text())
    except json.JSONDecodeError:
        return []
    
    return _normalize_cookies(data)


def parse_cookies_from_string(string: Optional[str]) -> list[dict]:
    """
    Получение списка cookie из строки JSON (формат Cookie Editor).

    :param string: JSON-строка с куками от Cookie Editor
    :return: Список словарей cookie
    """
    if not string:
        return []
    
    try:
        data = json.loads(string)
    except json.JSONDecodeError:
        return []
    
    return _normalize_cookies(data)


def _normalize_cookies(data) -> list[dict]:
    """
    Приводит разные форматы кук к единому списку словарей.

    Поддерживаемые форматы:
    - Массив объектов Cookie Editor (основной)
    - Объект с ключом 'cookies' (старый формат)
    """
    if isinstance(data, list):
        return data
    
    if isinstance(data, dict):
        if "cookies" in data:
            return data["cookies"]
        # Если это одиночный объект куки — оборачиваем в массив
        if "name" in data and "value" in data:
            return [data]
    
    return []


def save_cookies_to_file(cookies: list[dict], filepath: Path) -> None:
    """
    Сохранение списка cookie в файл.

    :param cookies: Список словарей cookie
    :param filepath: Путь к файлу для сохранения
    """
    filepath.write_text(json.dumps(cookies, indent=2))