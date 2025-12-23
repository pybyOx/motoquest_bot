
def get_kwargs(keys: tuple, data: dict) -> tuple:
    """Проверяет наличие ключей в словаре и возвращает значения в указанном порядке.
    :param keys: Кортеж ключей в нужном порядке.
    :param data: Словарь, из которого нужно извлечь значения.
    :return : Возвращает значения в указанном порядке
    :raises KeyError: Если какие-то ключи отсутствуют.
    """
    missing = set(keys) - data.keys()
    if missing:
        raise KeyError(f"Отсутствуют ключи: {', '.join(missing)}")
    return tuple(data[key] for key in keys)
