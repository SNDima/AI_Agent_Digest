"""
Database operations for search summaries.
"""

import sqlite3
from typing import Optional
from models.search_summary import SearchSummary
from utils.config import get_database_file


def save_search_summary(summary: SearchSummary, config_path: str) -> None:
    """Save a search summary to the database."""
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO search_summaries (summary_text)
            VALUES (?)
            """,
            (summary.summary_text,)
        )
        conn.commit()
    finally:
        conn.close()
