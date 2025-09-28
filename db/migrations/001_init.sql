-- 001_init.sql
CREATE TABLE rss_entries (
    guid TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    summary TEXT,
    author TEXT,
    categories TEXT,
    published_at DATETIME,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    posted BOOLEAN DEFAULT 0
);

CREATE INDEX idx_posted ON rss_entries (posted);
CREATE INDEX idx_published_at ON rss_entries (published_at);
CREATE INDEX idx_fetched_at ON rss_entries (fetched_at);
