-- Phase 2 & 3: Stop Secret Exposure & Migrate Keys
-- Add new columns for credential hashing and metadata idempotently

DELIMITER //

CREATE PROCEDURE migrate_api_credentials()
BEGIN
    -- Add public_key_id if not exists
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'api_credentials' AND COLUMN_NAME = 'public_key_id') THEN
        ALTER TABLE api_credentials ADD COLUMN public_key_id VARCHAR(20) AFTER user_id;
    END IF;

    -- Add secret_hash if not exists
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'api_credentials' AND COLUMN_NAME = 'secret_hash') THEN
        ALTER TABLE api_credentials ADD COLUMN secret_hash VARCHAR(128) AFTER public_key_id;
    END IF;

    -- Add key_last_four if not exists
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'api_credentials' AND COLUMN_NAME = 'key_last_four') THEN
        ALTER TABLE api_credentials ADD COLUMN key_last_four CHAR(4) AFTER secret_hash;
    END IF;

    -- Add updated_at if not exists
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'api_credentials' AND COLUMN_NAME = 'updated_at') THEN
        ALTER TABLE api_credentials ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
    END IF;

    -- Add revoked_at if not exists
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'api_credentials' AND COLUMN_NAME = 'revoked_at') THEN
        ALTER TABLE api_credentials ADD COLUMN revoked_at DATETIME DEFAULT NULL;
    END IF;

    -- Modify secret_key to allow NULL and add paused to status enum
    ALTER TABLE api_credentials MODIFY secret_key VARCHAR(64) NULL;
    ALTER TABLE api_credentials MODIFY status ENUM('active','paused','revoked') DEFAULT 'active';
END //

DELIMITER ;

CALL migrate_api_credentials();
DROP PROCEDURE migrate_api_credentials;


-- Phase 8: Audit Log
-- Create audit log table (CREATE TABLE IF NOT EXISTS is natively idempotent)
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
