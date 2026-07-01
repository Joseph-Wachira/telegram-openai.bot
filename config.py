import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))
DATABASE_PATH = os.getenv("DATABASE", "data/db.sqlite3")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", 20))
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 20))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
WEBHOOK_ENABLED = os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PORT = int(os.getenv("PORT", 8443))

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in .env")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")