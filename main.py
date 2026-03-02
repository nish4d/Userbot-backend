import asyncio
import logging
import signal
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import threading
from config import Config
from database import get_reply_rules, is_user_blacklisted
from utils.humanize import send_typing_action, random_delay
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
shutdown_event = asyncio.Event()

# Setup event loop for Windows compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Initialize FastAPI app
app = FastAPI(title="Telegram Userbot API", version="1.0.0")

# Redirect root to API root
@app.get("/")
async def redirect_to_api():
    return RedirectResponse(url="/api")

# Import routes after app initialization to avoid circular imports
from api.routes import router as api_router
app.include_router(api_router)

async def process_message(client, message):
    """Process incoming messages and send auto-replies"""
    # Ignore if message is from ourselves or not a private chat
    from pyrogram.enums import ChatType
    if message.from_user.is_self or message.chat.type != ChatType.PRIVATE:
        return
    
    # Ignore if no text in message
    if not message.text:
        return
    
    # Check if user is blacklisted
    if is_user_blacklisted(message.from_user.id):
        return
    
    # Get all reply rules
    rules = get_reply_rules()
    
    # Find matching rule
    response_text = None
    matched_rule = None
    for rule in rules:
        if not rule.get("enabled", True):
            continue
            
        # Handle both old single trigger and new multiple triggers format
        triggers = rule.get("triggers")
        if triggers is None:
            # Backward compatibility: check for old "trigger" field
            trigger = rule.get("trigger")
            if trigger:
                triggers = [trigger]
            else:
                triggers = []
        
        # Check if any of the triggers match the message
        for trigger in triggers:
            if trigger and trigger.lower() in message.text.lower():
                response_text = rule.get("response")
                matched_rule = rule
                break
        
        if response_text:
            break
    
    # If no specific trigger matched, use "any" rule (if it exists)
    if not response_text:
        for rule in rules:
            # Handle both old single trigger and new multiple triggers format
            triggers = rule.get("triggers")
            if triggers is None:
                # Backward compatibility: check for old "trigger" field
                trigger = rule.get("trigger")
                if trigger:
                    triggers = [trigger]
                else:
                    triggers = []
            
            # Check if this is an "any" rule
            if "any" in triggers and rule.get("enabled", True):
                response_text = rule.get("response")
                matched_rule = rule
                break
    
    # If we have a response, send it with human-like behavior
    if response_text and matched_rule:
        # Send typing action
        await send_typing_action(client, message.chat.id)
        
        # Add random delay to seem human
        await random_delay()
        
        # Check if we have an image URL
        image_url = matched_rule.get("image_url")
        
        # Send the reply with or without image
        from pyrogram.enums import ParseMode
        if image_url:
            # Send photo with caption
            await client.send_photo(
                chat_id=message.chat.id,
                photo=image_url,
                caption=response_text,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Send text message only
            await client.send_message(
                chat_id=message.chat.id,
                text=response_text,
                parse_mode=ParseMode.MARKDOWN
            )

def start_fastapi():
    """Start FastAPI server in a separate thread"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.PORT,
        log_level="info"
    )

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    # Cancel all tasks and stop the event loop
    for task in asyncio.all_tasks():
        task.cancel()

async def idle():
    """Custom idle function to keep the client running"""
    while True:
        await asyncio.sleep(1)

async def main():
    """Main function to start the userbot"""
    # Import Pyrogram here to avoid event loop issues
    from pyrogram import Client
    import pyrogram.handlers
    from pyrogram.errors import FloodWait
    from pyrogram import filters
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if session string is provided
    session_string = os.getenv("SESSION_STRING")
    
    if session_string:
        logger.info("Using session string from environment variable")
        # Initialize Pyrogram client with session string
        client = Client(
            "userbot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=session_string
        )
    else:
        logger.info("Using session file")
        # Initialize Pyrogram client with phone number (for file-based session)
        client = Client(
            "userbot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            phone_number=Config.PHONE
        )
    
    # Define the message handler function
    async def handle_message(client, message):
        """Handle incoming messages"""
        try:
            await process_message(client, message)
        except FloodWait as e:
            logger.warning(f"FloodWait received. Sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
    
    # Register the message handler with filters to listen to all private messages
    client.add_handler(pyrogram.handlers.MessageHandler(handle_message, filters.private))
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Start Pyrogram client
    await client.start()
    logger.info("Userbot started!")
    
    # Log information about the client
    me = await client.get_me()
    logger.info(f"Connected as {me.first_name} ({me.id})")
    
    # Keep the client running
    try:
        await idle()
    except asyncio.CancelledError:
        pass
    finally:
        # Stop the client
        await client.stop()
        logger.info("Userbot stopped!")

if __name__ == "__main__":
    try:
        # Create and set event loop before importing pyrogram
        if sys.platform == "win32":
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")