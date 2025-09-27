import feedparser
import logging
from typing import List, Dict
import yaml
from pathlib import Path
from dateutil import parser as date_parser
from models.article import Article

logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict:
    """Load YAML configuration file and validate it."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not config or "sources" not in config:
        raise ValueError(f"Invalid config file: missing 'sources' key in {config_path}")

    if not isinstance(config["sources"], list) or len(config["sources"]) == 0:
        raise ValueError(f"Invalid config file: 'sources' must be a non-empty list in {config_path}")

    if not any(source.get("enabled", False) for source in config["sources"]):
        raise ValueError(f"Invalid config file: at least one source must be enabled in {config_path}")

    return config


def fetch_rss_articles(url: str, source_name: str) -> List[Article]:
    """Fetch articles from an RSS feed URL."""
    logger.info(f"Fetching RSS feed from {url}...")
    feed = feedparser.parse(url)

    if feed.bozo:
        logger.warning(f"Parsing irregularity in feed {url}: {feed.bozo_exception}")

    if not getattr(feed, "entries", None):
        logger.error(f"No entries found in feed {url}")
        return []

    articles = []
    for entry in feed.entries:
        # Parse published date if available
        published_at = None
        if hasattr(entry, 'published'):
            try:
                published_at = date_parser.parse(entry.published)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse published date: {entry.published}")
        
        # Create Article object
        article = Article(
            guid=getattr(entry, "id", entry.link),  # fallback to link if no id
            source=source_name,
            title=entry.title,
            link=entry.link,
            summary=getattr(entry, "summary", None),
            author=getattr(entry, "author", None),
            categories=[tag.term for tag in getattr(entry, "tags", [])],
            published_at=published_at
        )
        articles.append(article)
        logger.debug(f"Fetched article: {article.title}")

    logger.info(f"Fetched {len(articles)} articles from {url}.")
    return articles


def load_all_articles(config_path: str) -> List[Article]:
    """
    Load articles from all enabled sources defined in the config.
    Returns a flat list of article dictionaries.
    """
    config = load_config(config_path)
    all_articles: List[Article] = []

    for source in config["sources"]:
        if not source.get("enabled", False):
            continue

        source_type = source.get("type")
        url = source.get("url")
        source_name = source.get("name")

        if source_type == "rss" and url:
            articles = fetch_rss_articles(url, source_name)
            all_articles.extend(articles)
        else:
            logger.warning(f"Unsupported source type or missing URL: {source}")

    logger.info(f"Total collected articles: {len(all_articles)}")
    return all_articles


# to test locally
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    try:
        articles = load_all_articles("config/sources.yaml")
    except (FileNotFoundError, ValueError) as e:
        logger.critical(str(e))
        raise

    for a in articles[:3]:  # print first 3
        print(f"- {a.title} ({a.link}) by {a.author}")
