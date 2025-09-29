"""
Time utility functions for checking search conditions.
"""

import logging
from datetime import datetime, time, timezone, timedelta
from typing import Optional


def is_search_time_reached(search_time_utc: str) -> bool:
    """Check if current time has reached the configured search time."""
    try:
        # Parse search time
        search_hour, search_minute = map(int, search_time_utc.split(":"))
        search_time = time(search_hour, search_minute)
        
        # Get current UTC time
        utc_now = datetime.now(timezone.utc)
        current_time = utc_now.time()
        
        return current_time >= search_time
    except (ValueError, IndexError) as e:
        logging.error(f"Invalid search time format '{search_time_utc}': {e}")
        return False


def was_search_run_today(last_datetime: Optional[datetime]) -> bool:
    """Check if search was already run today."""
    if not last_datetime:
        return False
    
    today = datetime.now(timezone.utc).date()
    return last_datetime.date() == today
    """Check if search should run based on date and time conditions."""
    # Check if search was already run today
    if was_search_run_today(last_datetime):
        logging.info(f"Search already run today ({last_datetime.date()}), skipping...")
        return False
    
    # Check if it's time to run the search
    if not is_search_time_reached(search_time_utc):
        logging.info(f"Current time is before search time {search_time_utc} UTC, skipping...")
        return False
    
    logging.info(f"Search conditions met - current time is after {search_time_utc} UTC")
    return True


def should_run_delivery(last_datetime: Optional[datetime], delivery_time_utc: str) -> bool:
    """Check if delivery should run based on date and time conditions."""
    # Check if delivery was already run today
    if was_search_run_today(last_datetime):
        logging.info(f"Delivery already run today ({last_datetime.date()}), skipping...")
        return False
    
    # Check if it's time to run the delivery
    if not is_search_time_reached(delivery_time_utc):
        logging.info(f"Current time is before delivery time {delivery_time_utc} UTC, skipping...")
        return False
    
    logging.info(f"Delivery conditions met - current time is after {delivery_time_utc} UTC")
    return True


def parse_articles_freshness(freshness: str) -> datetime:
    """Parse articles_freshness string to get cutoff datetime."""
    now = datetime.now()
    
    if freshness == "last_1h":
        return now - timedelta(hours=1)
    elif freshness == "last_24h":
        return now - timedelta(hours=24)
    elif freshness == "last_7d":
        return now - timedelta(days=7)
    elif freshness == "last_30d":
        return now - timedelta(days=30)
    else:
        # Default to 24 hours if unknown format
        return now - timedelta(hours=24)
