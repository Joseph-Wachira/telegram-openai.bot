import openai
from config import OPENAI_API_KEY
import asyncio
from utils.logger import logger

client = openai.OpenAI(api_key=OPENAI_API_KEY)

async def generate_image(prompt: str, size: str = "1024x1024") -> str:
    """Return image URL."""
    try:
        response = await asyncio.to_thread(
            lambda: client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"DALL-E error: {e}", exc_info=True)
        raise