from telegram import Update
from telegram.ext import ContextTypes
from services.openai_service import chat_completion
from utils.rate_limit import rate_limiter
from utils.markdown import escape_markdown
from utils.logger import logger
from database import update_user

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not rate_limiter.is_allowed(user.id):
        await update.message.reply_text("⚠️ Rate limit exceeded. Please wait a minute.")
        return

    update_user(user.id, user.username, user.first_name)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = await chat_completion(user.id, update.message.text)
        safe_reply = escape_markdown(reply)
        await update.message.reply_text(safe_reply, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await update.message.reply_text("Sorry, something went wrong. Please try again.")