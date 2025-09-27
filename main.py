import logging
from typing import List

from sources.loader import load_all_articles
from models.article import Article
from processing import filters
from storage import store
from delivery import telegram
from utils.constants import DATABASE_CONFIG_PATH, SOURCES_CONFIG_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
)


def fetch_sources() -> List[Article]:
    logging.info("Fetching sources...")
    articles = load_all_articles(SOURCES_CONFIG_PATH)
    return articles


def process_content(items: List[Article]) -> List[Article]:
    logging.info("Processing content...")
    filtered = filters.filter_items(items)
    return filtered


def store_content(items: List[Article]) -> None:
    logging.info("Storing content...")
    store.save(items, DATABASE_CONFIG_PATH)


def deliver_digest(items: List[Article]) -> None:
    logging.info("Delivering digest...")
    telegram.send(items)


def main() -> None:
    logging.info("AI Agent Digest started")

    try:
        articles = fetch_sources()
        processed = process_content(articles)
        store_content(processed)
        deliver_digest(processed)
    except Exception as e:
        logging.error(f"Pipeline failed: {e}", exc_info=True)
        raise # re-raise to stop execution

    logging.info("AI Agent Digest finished")


if __name__ == "__main__":
    main()
