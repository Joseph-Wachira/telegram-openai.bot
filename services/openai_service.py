import openai
from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_HISTORY
from utils.logger import logger
import asyncio
from typing import List, Dict, Optional

client = openai.OpenAI(api_key=OPENAI_API_KEY)

conversations = {}

def get_conversation(user_id: int) -> List[Dict[str, str]]:
    return conversations.setdefault(user_id, [])

def clear_conversation(user_id: int):
    conversations.pop(user_id, None)

def add_message(user_id: int, role: str, content: str):
    conv = get_conversation(user_id)
    conv.append({"role": role, "content": content})
    system_msgs = [m for m in conv if m["role"] == "system"]
    other_msgs = [m for m in conv if m["role"] != "system"]
    if len(other_msgs) > MAX_HISTORY:
        other_msgs = other_msgs[-MAX_HISTORY:]
    conversations[user_id] = system_msgs + other_msgs

async def chat_completion(user_id: int, user_message: str, model: Optional[str] = None) -> str:
    model = model or OPENAI_MODEL
    add_message(user_id, "user", user_message)
    messages = get_conversation(user_id)
    try:
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
        )
        reply = response.choices[0].message.content
        add_message(user_id, "assistant", reply)
        tokens = response.usage.total_tokens
        from database import update_token_usage
        update_token_usage(user_id, tokens)
        return reply
    except Exception as e:
        logger.error(f"OpenAI chat error for user {user_id}: {e}", exc_info=True)
        raise

async def vision_analysis(image_url: str, caption: Optional[str] = None) -> str:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": caption or "What's in this image?"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]
    try:
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Vision API error: {e}", exc_info=True)
        raise