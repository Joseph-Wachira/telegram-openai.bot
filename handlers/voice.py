import os
from telegram import Update
from telegram.ext import ContextTypes
from services.transcription import transcribe_audio
from services.openai_service import chat_completion
from utils.rate_limit import rate_limiter
from utils.logger import logger
from database import update_user

ALLOWED_AUDIO_EXTENSIONS = ['.ogg', '.mp3', '.wav', '.m4a']
MAX_FILE_SIZE = 20 * 1024 * 1024

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not rate_limiter.is_allowed(user.id):
        await update.message.reply_text("⚠️ Rate limit exceeded.")
        return

    update_user(user.id, user.username, user.first_name)
    voice = update.message.voice or update.message.audio
    if not voice:
        await update.message.reply_text("Please send a voice message or audio file.")
        return

    if voice.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("File too large. Maximum size is 20MB.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    file = await context.bot.get_file(voice.file_id)
    file_ext = os.path.splitext(file.file_path)[1].lower()
    if file_ext not in ALLOWED_AUDIO_EXTENSIONS:
        await update.message.reply_text("Unsupported audio format. Supported: OGG, MP3, WAV, M4A")
        return

    temp_path = f"temp_audio_{user.id}{file_ext}"
    try:
        await file.download_to_drive(temp_path)
        transcription = await transcribe_audio(temp_path)
        await update.message.reply_text(f"Transcription: {transcription}")
        reply = await chat_completion(user.id, transcription)
        from utils.markdown import escape_markdown
        await update.message.reply_text(escape_markdown(reply), parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Voice handling error: {e}")
        await update.message.reply_text("Error processing voice message.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)