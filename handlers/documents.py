import os
from telegram import Update
from telegram.ext import ContextTypes
from services.openai_service import chat_completion
from utils.rate_limit import rate_limiter
from utils.logger import logger
from database import update_user
import PyPDF2
import docx

ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.docx']
MAX_FILE_SIZE = 10 * 1024 * 1024

def extract_text_from_pdf(file_path: str) -> str:
    text = []
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text.append(page.extract_text())
    return "\n".join(text)

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not rate_limiter.is_allowed(user.id):
        await update.message.reply_text("⚠️ Rate limit exceeded.")
        return

    update_user(user.id, user.username, user.first_name)
    document = update.message.document
    if document.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("File too large. Max 10MB.")
        return

    file_ext = os.path.splitext(document.file_name)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        await update.message.reply_text("Unsupported format. Use PDF, TXT, or DOCX.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    file = await context.bot.get_file(document.file_id)
    temp_path = f"temp_doc_{user.id}{file_ext}"
    try:
        await file.download_to_drive(temp_path)
        if file_ext == '.pdf':
            text = extract_text_from_pdf(temp_path)
        elif file_ext == '.docx':
            text = extract_text_from_docx(temp_path)
        else:
            with open(temp_path, 'r', encoding='utf-8') as f:
                text = f.read()

        question = update.message.caption or "Summarize this document."
        prompt = f"Document content:\n{text[:4000]}\n\nUser question: {question}"
        reply = await chat_completion(user.id, prompt)
        from utils.markdown import escape_markdown
        await update.message.reply_text(escape_markdown(reply), parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Document error: {e}")
        await update.message.reply_text("Error processing document.")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)