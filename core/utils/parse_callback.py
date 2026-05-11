def parse_callback_data(data: str) -> tuple[str, str | None]:
    """
    Разбирает строку callback_data на тип события и полезную нагрузку.

    Ожидаемый формат строки:
        "<callback_type>:<payload>"

    Если символ ":" отсутствует, вся строка интерпретируется
    как callback_type, а payload устанавливается в None.

    :param data: Строка callback_data, полученная из Telegram.

    :return: Кортеж (callback_type, payload)
        - callback_type (str): тип события
        - payload (str | None): данные после ":", либо None

    """
    if ":" in data:
        callback_type, payload = data.split(":", 1)
    else:
        callback_type, payload = data, None
    return callback_type, payload
