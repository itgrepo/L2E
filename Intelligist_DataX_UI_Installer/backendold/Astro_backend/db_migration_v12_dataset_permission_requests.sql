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

