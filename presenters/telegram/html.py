import html


def bold(text: str) -> str:
    return f"<b>{html.escape(text)}</b>"
