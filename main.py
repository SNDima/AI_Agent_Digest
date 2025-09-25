import logging
from typing import List, Dict

from sources.loader import load_all_articles
from processing import filters
from storage import store
from delivery import telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
)


def fetch_sources() -> List[Dict]:
    logging.info("Fetching sources...")
    items: List[Dict] = []
    articles = load_all_articles("config/sources.yaml")
    items.extend(articles)
    return items


def process_content(items: List[Dict]) -> List[Dict]:
    logging.info("Processing content...")
    filtered = filters.filter_items(items)
    return filtered


def store_content(items: List[Dict]) -> None:
    logging.info("Storing content...")
    store.save(items)


def deliver_digest(items: List[Dict]) -> None:
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
