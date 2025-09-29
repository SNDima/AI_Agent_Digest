import sqlite3
from typing import List
from datetime import datetime
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


def get_articles_after(config_path: str, after_datetime: datetime) -> List[Article]:
    """
    Get articles with published_at later than the given datetime.
    
    Args:
        config_path: Path to the database configuration file
        after_datetime: Only return articles published after this datetime
        
    Returns:
        List of Article objects published after the given datetime
    """
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT guid, source, title, link, summary, author, categories, published_at, fetched_at, posted, relevance_score
            FROM rss_entries
            WHERE published_at > ?
            ORDER BY published_at DESC
            """,
            (after_datetime.isoformat(),)
        )
        
        articles = []
        for row in cursor.fetchall():
            # Parse categories from comma-separated string
            categories = row['categories'].split(',') if row['categories'] else []
            
            # Parse published_at datetime
            published_at = None
            if row['published_at']:
                published_at = datetime.fromisoformat(row['published_at'].replace('Z', '+00:00'))
            
            # Parse fetched_at datetime
            fetched_at = None
            if row['fetched_at']:
                fetched_at = datetime.fromisoformat(row['fetched_at'].replace('Z', '+00:00'))
            
            article = Article(
                guid=row['guid'],
                source=row['source'],
                title=row['title'],
                link=row['link'],
                summary=row['summary'],
                author=row['author'],
                categories=categories,
                published_at=published_at,
                fetched_at=fetched_at,
                posted=bool(row['posted']),
                relevance_score=row['relevance_score']
            )
            articles.append(article)
        
        return articles
    finally:
        conn.close()


def update_relevance_scores(articles: List[Article], config_path: str) -> None:
    """
    Update relevance scores for articles in the database.
    
    Args:
        articles: List of Article objects with relevance_score populated
        config_path: Path to the database configuration file
    """
    if not articles:
        return
        
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        
        # Prepare data for batch update
        batch_data = []
        for article in articles:
            if article.relevance_score is not None:
                batch_data.append((
                    article.relevance_score,
                    article.guid
                ))
        
        if not batch_data:
            return
        
        # Execute batch update
        cursor.executemany(
            """
            UPDATE rss_entries 
            SET relevance_score = ?
            WHERE guid = ?
            """,
            batch_data
        )
        conn.commit()
        
    finally:
        conn.close()