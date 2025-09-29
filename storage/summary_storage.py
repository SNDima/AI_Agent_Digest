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


def get_latest_search_summary(config_path: str) -> Optional[SearchSummary]:
    """Get the latest search summary from the database."""
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, summary_text, fetched_at
            FROM search_summaries
            ORDER BY fetched_at DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if row:
            return SearchSummary(
                summary_text=row['summary_text'],
                fetched_at=row['fetched_at']
            )
        return None
    finally:
        conn.close()
