-- 002_create_search_summaries.sql
CREATE TABLE search_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_text TEXT NOT NULL,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fetched_at_search ON search_summaries (fetched_at);
