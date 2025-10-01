"""
Database operations for search results.
"""

import sqlite3
from typing import List
from models.search_result import SearchResult
from utils.config import get_database_file


def save_search_results(search_results: List[SearchResult], config_path: str) -> None:
    """Save a list of SearchResult objects to the database."""
    if not search_results:
        return
        
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        
        # Prepare data for batch insertion
        batch_data = []
        for result in search_results:
            batch_data.append((
                result.title,
                result.snippet,
                result.source,
                result.published_date,
                str(result.link)
            ))
        
        # Batch insert with conflict resolution (ignore duplicates based on title + source)
        cursor.executemany(
            """
            INSERT OR IGNORE INTO search_results 
            (title, snippet, source, published_date, link)
            VALUES (?, ?, ?, ?, ?)
            """,
            batch_data
        )
        
        conn.commit()
    finally:
        conn.close()
