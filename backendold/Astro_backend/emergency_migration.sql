-- Phase 2 & 3: Stop Secret Exposure & Migrate Keys
-- Add new columns for credential hashing and metadata
ALTER TABLE api_credentials 
ADD COLUMN public_key_id VARCHAR(20) AFTER user_id,
ADD COLUMN secret_hash VARCHAR(128) AFTER public_key_id,
ADD COLUMN key_last_four CHAR(4) AFTER secret_hash,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD COLUMN revoked_at DATETIME DEFAULT NULL;

-- Phase 8: Audit Log
-- Create audit log table
CREATE TABLE IF NOT EXISTS api_audit_log (
    audit_id        INT AUTO_INCREMENT PRIMARY KEY,
    actor_user_id   INT NOT NULL,
    target_user_id  INT DEFAULT NULL,
    service_id      INT DEFAULT NULL,
    credential_id   INT DEFAULT NULL,
    action          VARCHAR(50) NOT NULL,
    before_data     JSON DEFAULT NULL,
    after_data      JSON DEFAULT NULL,
    result          VARCHAR(20) NOT NULL DEFAULT 'success',
    ip_address      VARCHAR(45),
    user_agent      VARCHAR(500),
    request_id      VARCHAR(36),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_actor (actor_user_id),
    INDEX idx_service (service_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
);
