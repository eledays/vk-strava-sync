from logging import Logger


def log_message_handling(logger: Logger, name: str, user_id: str | int, text: str) -> None:
    """
    Логирование обработки сообщения

    :param logger: Объект логгера
    :param name: Имя модуля (__name__)
    :param user_id: VK-ID пользователя
    :param text: Текст сообщения (будет обрезан до 20 символов)
    """
    logger.info(
        f'Сообщение обработано ({name.split(".")[-1]}) от {user_id}: '
        f'{text[:20]}{"..." if len(text) > 20 else ""}'
    )
