import re

def escape_markdown(text: str) -> str:
    """Escape Telegram MarkdownV2 special characters."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def bold(text: str) -> str:
    return f"*{text}*"

def code(text: str) -> str:
    return f"`{text}`"
