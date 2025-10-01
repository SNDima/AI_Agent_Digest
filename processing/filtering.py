"""
Article filtering module for selecting top articles based on relevance scores.
"""

import logging
from typing import List
from models.article import Article


def filter_top_articles(scored_articles: List[Article]) -> List[Article]:
    """
    Filter and order articles by relevance score.
    
    Selection criteria:
    - If at least 5 articles have high relevance (score > 80): select top 5
    - If less than 5 articles have high relevance: select top 3
    - Articles with None scores are filtered out
    
    Args:
        scored_articles: List of Article objects with relevance scores and reasoning
        
    Returns:
        List of top Article objects selected based on relevance scores
    """
    logging.info("Filtering top articles by relevance score...")
    
    if not scored_articles:
        logging.warning("No articles to filter")
        return []
    
    # Filter articles with valid scores and sort by score descending
    valid_articles = [article for article in scored_articles if article.relevance_score is not None]
    sorted_articles = sorted(valid_articles, key=lambda x: x.relevance_score, reverse=True)
    
    if not sorted_articles:
        logging.warning("No articles with valid relevance scores")
        return []
    
    # Check if there are at least 5 articles with high relevance (score > 80)
    high_relevance_articles = [article for article in sorted_articles if article.relevance_score > 80]
    
    if len(high_relevance_articles) >= 5:
        # At least 5 articles have high relevance, take top 5
        top_articles = sorted_articles[:5]
        logging.info(f"At least 5 articles have high relevance (>80), selected top {len(top_articles)} articles")
    else:
        # Less than 5 articles have high relevance, take top 3
        top_articles = sorted_articles[:3]
        logging.info(f"Less than 5 articles have high relevance (>80), selected top {len(top_articles)} articles")
    
    # Log the selected articles
    for i, article in enumerate(top_articles, 1):
        reasoning_preview = article.reasoning[:100] + "..." if article.reasoning and len(article.reasoning) > 100 else article.reasoning or "No reasoning"
        logging.info(f"Selected article {i}: '{article.title}' (score: {article.relevance_score}) - {reasoning_preview}")
    
    return top_articles
