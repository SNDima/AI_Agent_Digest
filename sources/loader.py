import feedparser
import logging
from typing import List, Dict
import yaml
from pathlib import Path

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


def fetch_rss_articles(url: str) -> List[Dict]:
    """
    Fetch articles from an RSS feed.
    Returns a list of dicts with title, link, published date, summary, author, guid, and categories.
    """
    logger.info(f"Fetching RSS feed from {url}...")
    
    feed = feedparser.parse(url)

    if feed.bozo:  # bozo flag means parsing issue
        logger.error(f"Error parsing feed: {feed.bozo_exception}")
        return []

    articles = []
    for entry in feed.entries:
        article = {
            "guid": getattr(entry, "id", None),
            "title": entry.title,
            "link": entry.link,
            "published": getattr(entry, "published", None),
            "summary": getattr(entry, "summary", None),
            "author": getattr(entry, "author", None),
            "categories": [tag.term for tag in getattr(entry, "tags", [])],
        }
        articles.append(article)
        logger.debug(f"Fetched article: {article}")

    logger.info(f"Fetched {len(articles)} articles from {url}.")
    return articles


def load_all_articles(config_path: str) -> List[Dict]:
    """
    Load articles from all enabled sources defined in the config.
    Returns a flat list of article dictionaries.
    """
    config = load_config(config_path)
    all_articles: List[Dict] = []

    for source in config["sources"]:
        if not source.get("enabled", False):
            continue

        source_type = source.get("type")
        url = source.get("url")

        if source_type == "rss" and url:
            articles = fetch_rss_articles(url)
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
        print(f"- {a['title']} ({a['link']}) by {a['author']} [{', '.join(a['categories'])}]")
