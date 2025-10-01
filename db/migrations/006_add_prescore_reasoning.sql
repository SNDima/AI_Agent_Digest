-- 006_add_prescore_reasoning.sql
-- Add relevance_prescore and reasoning columns to rss_entries table

ALTER TABLE rss_entries ADD COLUMN relevance_prescore INTEGER;
ALTER TABLE rss_entries ADD COLUMN reasoning TEXT;

-- Add index for efficient querying by relevance prescore
CREATE INDEX idx_relevance_prescore ON rss_entries (relevance_prescore);
