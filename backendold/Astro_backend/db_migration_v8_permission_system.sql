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
