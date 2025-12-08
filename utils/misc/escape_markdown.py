def escape_markdown(text: str) -> str:
    """
    Экранирует спецсимволы Markdown (v1), чтобы Telegram не ругался на форматирование.
    """
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)
