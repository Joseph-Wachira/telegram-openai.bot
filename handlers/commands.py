from telegram import Update
from telegram.ext import ContextTypes
from services.openai_service import clear_conversation
from database import get_user_stats
from config import OPENAI_MODEL, MAX_HISTORY
from utils.markdown import escape_markdown, bold

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = f"Hello {user.first_name}! I'm an AI bot powered by OpenAI.\nType /help for commands."
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"{bold('Available commands:')}\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/models - List available models\n"
        "/image <prompt> - Generate an image\n"
        "/clear - Reset conversation\n"
        "/stats - Your usage stats\n"
        "/about - About this bot\n"
        "\nYou can also send voice messages, images, and documents."
    )
    await update.message.reply_text(text, parse_mode="MarkdownV2")

async def models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    models_list = "GPT-4.1, GPT-4o, GPT-4-turbo, GPT-5 (if available)\nCurrent model: " + OPENAI_MODEL
    await update.message.reply_text(models_list)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_conversation(update.effective_user.id)
    await update.message.reply_text("Conversation history cleared.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = get_user_stats(user_id)
    if s:
        text = (
            f"User: {s.get('first_name')} (@{s.get('username')})\n"
            f"Requests: {s.get('request_count')}\n"
            f"Tokens used: {s.get('token_usage')}\n"
            f"Last seen: {s.get('last_seen')}"
        )
    else:
        
        text = "No stats yet."
    await update.message.reply_text(text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 Telegram AI Bot\n"
        "Powered by OpenAI GPT-4.1, DALL·E 3, Whisper, and Vision.\n"
        "Built with python-telegram-bot and OpenAI SDK.\n"
        "Max history: {} messages.".format(MAX_HISTORY)
    )
    await update.message.reply_text(about_text)