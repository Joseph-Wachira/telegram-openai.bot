import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_ENABLED, WEBHOOK_URL, PORT
from database import init_db
from handlers.chat import handle_message
from handlers.image import image_command
from handlers.voice import handle_voice
from handlers.vision import handle_photo
from handlers.documents import handle_document
from handlers.commands import start, help_command, models, clear, stats, about
from handlers.admin import broadcast, users_list, restart, shutdown, logs
from utils.logger import logger

def main():
    init_db()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("models", models))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("users", users_list))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("logs", logs))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    if WEBHOOK_ENABLED:
        logger.info("Starting webhook...")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TELEGRAM_BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
        )
    else:
        logger.info("Starting polling...")
        app.run_polling()

if __name__ == "__main__":
    main()