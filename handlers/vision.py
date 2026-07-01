from telegram import Update
from telegram.ext import ContextTypes
from services.openai_service import vision_analysis
from utils.rate_limit import rate_limiter
from utils.logger import logger
from database import update_user
import aiohttp
import base64

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not rate_limiter.is_allowed(user.id):
        await update.message.reply_text("⚠️ Rate limit exceeded.")
        return

    update_user(user.id, user.username, user.first_name)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    caption = update.message.caption
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(file.file_path) as resp:
            if resp.status != 200:
                await update.message.reply_text("Failed to download image.")
                return
            image_data = await resp.read()
    b64 = base64.b64encode(image_data).decode('utf-8')
    data_url = f"data:image/jpeg;base64,{b64}"

    try:
        analysis = await vision_analysis(data_url, caption)
        from utils.markdown import escape_markdown
        safe = escape_markdown(analysis)
        await update.message.reply_text(safe, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Vision error: {e}")
        await update.message.reply_text("Couldn't analyze image.")