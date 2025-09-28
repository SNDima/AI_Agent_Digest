"""
Time utility functions for checking search conditions.
"""

import logging
from datetime import datetime, time, timezone
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


def should_run_search(last_datetime: Optional[datetime], search_time_utc: str) -> bool:
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
