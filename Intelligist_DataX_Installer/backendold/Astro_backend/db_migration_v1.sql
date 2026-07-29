-- Migration to expand service table for Dataset Configuration


ALTER TABLE service 
ADD COLUMN IF NOT EXISTS dataset_id VARCHAR(50) AFTER service_id,
ADD COLUMN IF NOT EXISTS service_url TEXT AFTER service_name,
ADD COLUMN IF NOT EXISTS service_image LONGBLOB AFTER service_url,
ADD COLUMN IF NOT EXISTS category VARCHAR(100) AFTER service_image,
ADD COLUMN IF NOT EXISTS sub_category VARCHAR(100) AFTER category,
ADD COLUMN IF NOT EXISTS organization VARCHAR(255) AFTER sub_category,
ADD COLUMN IF NOT EXISTS accessibility VARCHAR(50) DEFAULT 'Public' AFTER organization,
ADD COLUMN IF NOT EXISTS contact_name VARCHAR(100) AFTER accessibility,
ADD COLUMN IF NOT EXISTS contact_email VARCHAR(100) AFTER contact_name,
ADD COLUMN IF NOT EXISTS tags TEXT AFTER contact_email,
ADD COLUMN IF NOT EXISTS purpose TEXT AFTER description;

-- Ensure status column matches what code expects if needed
-- Current DESCRIBE shows 'status', but code uses 'service_status' in INSERT
-- We will keep 'status' but update the code to use it correctly, or add an alias.
-- For safety, let's see if we should rename status or keep as is.
-- The DESCRIBE output showed 'status'. I will adjust the code to use 'status'.
