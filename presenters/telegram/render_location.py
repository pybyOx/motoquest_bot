import html


def render_location(url: str) -> str:
    safe_url = html.escape(str(url), quote=True)
    return f'<a href="{safe_url}">Место встречи</a>'
