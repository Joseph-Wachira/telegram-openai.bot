from telegram import Update
from telegram.ext import ContextTypes
from services.image_generation import generate_image
from utils.rate_limit import rate_limiter
from utils.logger import logger
from database import update_user

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not rate_limiter.is_allowed(user.id):
        await update.message.reply_text("⚠️ Rate limit exceeded. Please wait a minute.")
        return

    update_user(user.id, user.username, user.first_name)
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Please provide a prompt. Usage: /image <prompt>")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")
    try:
        image_url = await generate_image(prompt)
        await update.message.reply_photo(photo=image_url, caption=f"Generated: {prompt}")
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        await update.message.reply_text("Failed to generate image. Please try again later.")