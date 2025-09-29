"""
Database operations for deliveries.
"""

import sqlite3
from typing import Optional
from models.delivery import Delivery
from utils.config import get_database_file


def save_delivery(delivery: Delivery, config_path: str) -> None:
    """Save a delivery record to the database."""
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO deliveries (content, origin_message_id)
            VALUES (?, ?)
            """,
            (delivery.content, delivery.origin_message_id)
        )
        conn.commit()
    finally:
        conn.close()


def get_latest_delivery(config_path: str) -> Optional[Delivery]:
    """Get the latest delivery record from the database."""
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, delivered_at, content, origin_message_id
            FROM deliveries
            ORDER BY delivered_at DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if row:
            return Delivery(
                delivered_at=row['delivered_at'],
                content=row['content'],
                origin_message_id=row['origin_message_id']
            )
        return None
    finally:
        conn.close()
