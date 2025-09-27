import sqlite3
import os
from utils.config import get_database_file
from utils.constants import DATABASE_CONFIG_PATH, MIGRATIONS_DIR

def get_applied_migrations(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    rows = conn.execute("SELECT filename FROM schema_migrations").fetchall()
    return {row['filename'] for row in rows}

def apply_migration(conn, filename, sql):
    print(f"Applying {filename}...")
    conn.executescript(sql)
    conn.execute("INSERT INTO schema_migrations (filename) VALUES (?)", [filename])
    conn.commit()

def main(config_path: str):
    db_file = get_database_file(config_path)
    conn = sqlite3.connect(db_file)
    applied = get_applied_migrations(conn)

    migrations = sorted(os.listdir(MIGRATIONS_DIR))
    for filename in migrations:
        if filename not in applied and filename.endswith(".sql"):
            with open(os.path.join(MIGRATIONS_DIR, filename), "r", encoding="utf-8") as f:
                sql = f.read()
            apply_migration(conn, filename, sql)

    print("✅ All migrations applied.")

if __name__ == "__main__":
    main(DATABASE_CONFIG_PATH)
