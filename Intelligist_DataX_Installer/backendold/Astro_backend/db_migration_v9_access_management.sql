-- Migration v9: Dataset Access Management (By Group & By User)
-- Run against: psu_backend

-- 1. Table for Dataset-Group mapping
CREATE TABLE IF NOT EXISTS service_group_access (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    group_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_service_group (service_id, group_id),
    INDEX idx_service_id (service_id),
    INDEX idx_group_id (group_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Table for Dataset-User mapping
CREATE TABLE IF NOT EXISTS service_user_access (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_service_user (service_id, user_id),
    INDEX idx_service_id (service_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
