-- Migration to expand dataset metadata tables based on M-Society schema



-- Add new columns to 'service' table to support full Dataset Configuration
ALTER TABLE service 
ADD COLUMN IF NOT EXISTS sub_category VARCHAR(255) AFTER category,
ADD COLUMN IF NOT EXISTS dept_contact VARCHAR(255),
ADD COLUMN IF NOT EXISTS update_freq_unit VARCHAR(50),
ADD COLUMN IF NOT EXISTS update_freq_value INT,
ADD COLUMN IF NOT EXISTS geo_scope VARCHAR(255),
ADD COLUMN IF NOT EXISTS data_source VARCHAR(255),
ADD COLUMN IF NOT EXISTS data_format VARCHAR(255), -- Comma separated: csv, xlsx, json, etc.
ADD COLUMN IF NOT EXISTS gov_category VARCHAR(255),
ADD COLUMN IF NOT EXISTS license VARCHAR(255),
ADD COLUMN IF NOT EXISTS access_conditions TEXT,
ADD COLUMN IF NOT EXISTS sponsor VARCHAR(255),
ADD COLUMN IF NOT EXISTS smallest_unit VARCHAR(100),
ADD COLUMN IF NOT EXISTS url VARCHAR(500),
ADD COLUMN IF NOT EXISTS languages VARCHAR(255), -- Comma separated: Thai, English
ADD COLUMN IF NOT EXISTS objective_type VARCHAR(255), -- Strategy, Mission, Public, etc.
ADD COLUMN IF NOT EXISTS data_dictionary_path VARCHAR(255),
ADD COLUMN IF NOT EXISTS data_sampling_path VARCHAR(255),
ADD COLUMN IF NOT EXISTS external_dashboard_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS external_api_url VARCHAR(500);

-- Ensure default status is 'Active' if not already
ALTER TABLE service MODIFY COLUMN status VARCHAR(50) DEFAULT 'Active';

-- Create table for Category/Sub-category lookup if needed in future (Optional for now as we use static lists)
-- CREATE TABLE IF NOT EXISTS dataset_categories (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     category_name VARCHAR(255) NOT NULL,
--     sub_category_name VARCHAR(255)
-- );
