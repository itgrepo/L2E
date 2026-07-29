

-- Add tracking for credential expiration
ALTER TABLE api_credentials 
ADD COLUMN IF NOT EXISTS expires_at DATETIME DEFAULT NULL;
