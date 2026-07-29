-- Add apikey column to user table
ALTER TABLE user ADD COLUMN IF NOT EXISTS apikey VARCHAR(64) DEFAULT NULL;
