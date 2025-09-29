import logging
import os
from typing import List
from dotenv import load_dotenv
from models.article import Article

# Load environment variables from .env file
load_dotenv()

def send(post_text: str) -> None:
    """
    Send digest post to Telegram.
    Currently just prints info.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise ValueError("Telegram credentials (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID) must be set in environment variables")

    logging.info(f"Would send post to Telegram channel {chat_id}")
    logging.info(f"Post content:\n{post_text}")
