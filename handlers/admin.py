from telegram import Update
from telegram.ext import ContextTypes
from config import BOT_OWNER_ID
from utils.logger import logger
from database import get_all_users
import os

def is_owner(user_id: int) -> bool:
    return user_id == BOT_OWNER_ID

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    users = get_all_users()
    for u in users:
        try:
            await context.bot.send_message(chat_id=u['user_id'], text=message)
        except Exception as e:
            logger.error(f"Broadcast failed for {u['user_id']}: {e}")
    await update.message.reply_text(f"Broadcast sent to {len(users)} users.")

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("No users.")
        return
    text = "Users:\n" + "\n".join([f"{u['user_id']} @{u.get('username')} {u.get('first_name')}" for u in users[:50]])
    await update.message.reply_text(text[:4000])

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text("Restarting...")
    os._exit(0)

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text("Shutting down...")
    import sys
    sys.exit(0)

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    if os.path.exists("logs/bot.log"):
        with open("logs/bot.log", "rb") as f:
            await update.message.reply_document(document=f, filename="bot.log")
    else:
        await update.message.reply_text("No log file found.")