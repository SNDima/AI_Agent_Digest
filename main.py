import logging
from typing import List, Dict

from sources import techcrunch
from processing import filter
from storage import store
from delivery import telegram


def fetch_sources() -> List[Dict]:
    logging.info("Fetching sources...")
    items: List[Dict] = []
    items.extend(techcrunch.fetch())
    return items


def process_content(items: List[Dict]) -> List[Dict]:
    logging.info("Processing content...")
    filtered = filter.filter_items(items)
    return filtered


def store_content(items: List[Dict]) -> None:
    logging.info("Storing content...")
    store.save(items)


def deliver_digest(items: List[Dict]) -> None:
    logging.info("Delivering digest...")
    telegram.send(items)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    logging.info("AI Agent Digest started")

    items = fetch_sources()
    processed = process_content(items)
    store_content(processed)
    deliver_digest(processed)

    logging.info("AI Agent Digest finished")


if __name__ == "__main__":
    main()
