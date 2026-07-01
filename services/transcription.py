import openai
from config import OPENAI_API_KEY
import asyncio
from utils.logger import logger

client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def transcribe_audio(file_path: str) -> str:
    try:
        with open(file_path, "rb") as audio_file:
            transcript = await asyncio.to_thread(
                lambda: client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            )
        return transcript.text
    except Exception as e:
        logger.error(f"Whisper transcription error: {e}", exc_info=True)
        raise