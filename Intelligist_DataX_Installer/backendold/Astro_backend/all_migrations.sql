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
-- Database Migration v10: Monitor Optimization
-- Optimization for historical log viewing (up to 2 years)

-- 1. Index for basic monitoring queries (type filtering)
ALTER TABLE `log` ADD INDEX `idx_log_type` (`type`);

-- 2. Index for chronological retrieval and filtering (critical for 2-year range)
ALTER TABLE `log` ADD INDEX `idx_log_type_create` (`type`, `create_at`);

-- 3. Index for success/failure analysis
ALTER TABLE `log` ADD INDEX `idx_log_type_detail` (`type`, `log_detail`(20));
-- Migration v11: Organization Management
-- Run against: psu_backend

CREATE TABLE IF NOT EXISTS organization (
    org_id INT AUTO_INCREMENT PRIMARY KEY,
    org_name VARCHAR(255) NOT NULL,
    org_description TEXT,
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed some initial data for demonstration (optional, based on screenshot)
INSERT IGNORE INTO organization (org_name, org_description) VALUES
('กระทรวงการพัฒนาสังคมและความมั่นคงของมนุษย์', 'ปลัดกระทรวงการพัฒนาสังคมและควม...'),
('ทดสอบแก้ไข', 'ทดสอบแก้ไข'),
('Test', 'Test'),
('ทดสอบTest', 'ทดสอบTest'),
('องค์กรภายนอก', 'หน่วยงานเจ้าของข้อมูลจากองค์กรภาก...'),
('กรมกิจการเด็กและเยาวชน', 'หน่วยงานภายใต้กระทรวงการพัฒนา...');
-- Migration v12: Dataset Permission Requests
-- Run against: psu_backend

CREATE TABLE IF NOT EXISTS `dataset_permission_requests` (
  `request_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `service_id` INT NOT NULL,
  `fields_json` TEXT DEFAULT NULL,
  `reason` TEXT DEFAULT NULL,
  `status` VARCHAR(50) DEFAULT 'Pending',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `service` MODIFY COLUMN `api_type` ENUM('general', 'scope', 'public', 'private') DEFAULT 'public';

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
ALTER TABLE service 
ADD COLUMN date_start DATE DEFAULT NULL,
ADD COLUMN date_updated DATE DEFAULT NULL,
ADD COLUMN is_high_value VARCHAR(50) DEFAULT 'ไม่ใช่',
ADD COLUMN is_reference VARCHAR(50) DEFAULT 'ไม่ใช่';
ALTER TABLE service
ADD COLUMN dataset_type VARCHAR(50) DEFAULT 'record',
ADD COLUMN stat_year_start VARCHAR(10) DEFAULT NULL,
ADD COLUMN stat_year_latest VARCHAR(10) DEFAULT NULL,
ADD COLUMN stat_classification VARCHAR(255) DEFAULT NULL,
ADD COLUMN stat_unit VARCHAR(100) DEFAULT NULL,
ADD COLUMN stat_multiplier VARCHAR(100) DEFAULT NULL,
ADD COLUMN stat_calculation_method TEXT DEFAULT NULL,
ADD COLUMN stat_standard VARCHAR(255) DEFAULT NULL,
ADD COLUMN stat_official VARCHAR(50) DEFAULT 'ไม่ใช่',
ADD COLUMN geo_dataset_name VARCHAR(255) DEFAULT NULL,
ADD COLUMN geo_scale VARCHAR(100) DEFAULT NULL,
ADD COLUMN geo_west_bound VARCHAR(50) DEFAULT NULL,
ADD COLUMN geo_east_bound VARCHAR(50) DEFAULT NULL,
ADD COLUMN geo_north_bound VARCHAR(50) DEFAULT NULL,
ADD COLUMN geo_south_bound VARCHAR(50) DEFAULT NULL,
ADD COLUMN geo_position_accuracy VARCHAR(255) DEFAULT NULL,
ADD COLUMN geo_reference_time VARCHAR(255) DEFAULT NULL,
ADD COLUMN geo_published_date DATE DEFAULT NULL;
-- Add apikey column to user table
ALTER TABLE user ADD COLUMN IF NOT EXISTS apikey VARCHAR(64) DEFAULT NULL;
ALTER TABLE service
ADD COLUMN api_enabled BOOLEAN DEFAULT FALSE;
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


-- Add tracking for credential expiration
ALTER TABLE api_credentials 
ADD COLUMN IF NOT EXISTS expires_at DATETIME DEFAULT NULL;
-- db_migration_v8_permission_system.sql
-- Created: 2026-04-16
-- Purpose: Initialize the new Role-Based Permission System

-- 1. Create menu_name table to store system modules
CREATE TABLE IF NOT EXISTS `menu_name` (
  `menu_name_id` int(11) NOT NULL AUTO_INCREMENT,
  `menu_name` varchar(255) NOT NULL,
  `menu_desc` text,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`menu_name_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Create menu_permission table to map roles to menus
CREATE TABLE IF NOT EXISTS `menu_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `previlage_id` int(11) NOT NULL,
  `menu_name_id` int(11) NOT NULL,
  `value` varchar(10) DEFAULT 'No', -- 'Yes' or 'No'
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_role_menu` (`previlage_id`, `menu_name_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Populate menu_name with all current system menus
INSERT IGNORE INTO `menu_name` (menu_name) VALUES 
('Dashboard'),
('Data Catalog'),
('API Management'),
('User Approval'),
('Permission Management'),
('User Management'),
('Settings');

-- 4. Initialize Full Permissions for RootAdmin (previlage_id = 1)
INSERT IGNORE INTO `menu_permission` (previlage_id, menu_name_id, value)
SELECT 1, menu_name_id, 'Yes' FROM menu_name;

-- 5. Initialize Full Permissions for Admin (previlage_id = 2)
INSERT IGNORE INTO `menu_permission` (previlage_id, menu_name_id, value)
SELECT 2, menu_name_id, 'Yes' FROM menu_name;

-- 6. Initialize Restricted Permissions for regular User (previlage_id = 3)
INSERT IGNORE INTO `menu_permission` (previlage_id, menu_name_id, value)
SELECT 3, menu_name_id, 'No' FROM menu_name;

-- Standard users should have access to the Dashboard and Data Catalog by default
UPDATE `menu_permission` SET value = 'Yes' 
WHERE previlage_id = 3 AND menu_name_id IN (SELECT menu_name_id FROM menu_name WHERE menu_name IN ('Dashboard', 'Data Catalog'));
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
