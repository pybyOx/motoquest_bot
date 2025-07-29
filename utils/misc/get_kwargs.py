
def get_kwargs(keys: list, data: dict) -> tuple:
    """Проверяет наличие ключей в словаре и возвращает значения в указанном порядке"""
    missing = set(keys) - data.keys()
    if missing:
        raise KeyError(f"Отсутствуют ключи: {', '.join(missing)}")
    return tuple(data[key] for key in keys)
