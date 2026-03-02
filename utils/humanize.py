import asyncio
import random
import logging

logger = logging.getLogger(__name__)

async def send_typing_action(client, chat_id):
    """Send typing action to make the bot seem human"""
    try:
        # Import Pyrogram enums here to avoid event loop issues
        from pyrogram.enums import ChatAction
        await client.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception as e:
        logger.error(f"Failed to send typing action: {e}")

async def random_delay(min_seconds=2, max_seconds=8):
    """Add a random delay to make responses seem human"""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)