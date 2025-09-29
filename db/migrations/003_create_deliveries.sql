-- 003_create_deliveries.sql
CREATE TABLE deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    origin_message_id TEXT
);

CREATE INDEX idx_delivered_at_deliveries ON deliveries (delivered_at);
