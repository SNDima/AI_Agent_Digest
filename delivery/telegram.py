import logging
import os
from typing import List
from dotenv import load_dotenv
from models.article import Article
from telegram import Bot
from telegram.error import TelegramError

# Load environment variables from .env file
load_dotenv()

def send(post_text: str) -> int:
    """
    Send digest post to Telegram.
    
    Returns:
        int: The message ID of the sent message
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHANNEL")
    parse_mode = os.getenv("TELEGRAM_PARSE_MODE", "HTML")

    if not bot_token or not chat_id:
        raise ValueError("Telegram credentials (TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL) must be set in environment variables")

    try:
        # Create bot instance
        bot = Bot(token=bot_token)
        
        # Send message to Telegram
        logging.info(f"Sending post to Telegram channel {chat_id}")
        message = bot.send_message(
            chat_id=chat_id,
            text=post_text,
            parse_mode=parse_mode
        )
        
        logging.info(f"Successfully sent message to Telegram. Message ID: {message.message_id}")
        return message.message_id
        
    except TelegramError as e:
        logging.error(f"Failed to send message to Telegram: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error while sending to Telegram: {e}")
        raise
