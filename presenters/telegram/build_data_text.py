def build_data_text(data: dict) -> str:
    """Возвращает ссылку и текст(если есть) из словаря
    :param data: Словарь, содержащий ссылку на локацию (data["link"]) и опционально текст к ссылке (data["text"])
    """
    parts = []

    if data.get("text"):
        parts.append(data["text"])

    parts.append(f'📍 <a href="{data["link"]}">Открыть на карте</a>')

    return "\n\n".join(parts)
