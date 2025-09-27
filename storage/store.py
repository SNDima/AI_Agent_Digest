import sqlite3
from typing import List
from models.article import Article
from utils.config import get_database_file

def save(articles: List[Article], config_path: str) -> None:
    """
    Save a list of Article objects into the database using batch insertion.
    Articles are deduplicated by guid (already primary key in schema).
    """
    if not articles:
        return
        
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        
        # Prepare data for batch insertion
        batch_data = []
        for article in articles:
            batch_data.append((
                article.guid,
                article.source,
                article.title,
                str(article.link),
                article.summary,
                article.author,
                ",".join(article.categories) if article.categories else None,
                article.published_at.isoformat() if article.published_at else None,
            ))
        
        # Execute batch insertion
        cursor.executemany(
            """
            INSERT OR IGNORE INTO rss_entries
            (guid, source, title, link, summary, author, categories, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            batch_data
        )
        conn.commit()
    finally:
        conn.close()
