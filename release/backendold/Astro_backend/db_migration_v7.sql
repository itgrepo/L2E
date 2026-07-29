-- Migration v7: Advanced API Configuration & Scope Management
-- Run against: psu_backend


-- 1. Add API config columns to service table
ALTER TABLE service
ADD COLUMN IF NOT EXISTS api_type ENUM('general','scope') DEFAULT 'general',
ADD COLUMN IF NOT EXISTS api_endpoint VARCHAR(100) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS api_db_name VARCHAR(100) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS api_source_type ENUM('table','view') DEFAULT 'table',
ADD COLUMN IF NOT EXISTS api_source_name VARCHAR(100) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS api_request_fields JSON DEFAULT NULL,
ADD COLUMN IF NOT EXISTS api_response_fields JSON DEFAULT NULL;

-- 2. Create api_credentials table (per-user, per-service keys)
CREATE TABLE IF NOT EXISTS api_credentials (
    credential_id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    user_id INT NOT NULL,
    secret_key VARCHAR(64) NOT NULL,
    status ENUM('active','revoked') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_service_user (service_id, user_id),
    INDEX idx_secret_key (secret_key),
    INDEX idx_service_id (service_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Create api_scopes table (per-credential row-level filters)
CREATE TABLE IF NOT EXISTS api_scopes (
    scope_id INT AUTO_INCREMENT PRIMARY KEY,
    credential_id INT NOT NULL,
    scope_json JSON NOT NULL COMMENT '{"field_name": ["allowed_val1","allowed_val2"]}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_credential_id (credential_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
