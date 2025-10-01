-- 005_create_search_results.sql
CREATE TABLE search_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    snippet TEXT NOT NULL,
    source TEXT NOT NULL,
    published_date TEXT NOT NULL,
    link TEXT NOT NULL,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fetched_at_search_results ON search_results (fetched_at);
