-- 004_add_relevance_score.sql
-- Add relevance_score column to rss_entries table for AI agent content scoring

ALTER TABLE rss_entries ADD COLUMN relevance_score INTEGER;

-- Add index for efficient querying by relevance score
CREATE INDEX idx_relevance_score ON rss_entries (relevance_score);
