-- Migration v14: Google Authenticator (TOTP Two-Factor Authentication)
-- Creates user_two_factor table for storing TOTP secret keys and status

CREATE TABLE IF NOT EXISTS `user_two_factor` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL UNIQUE,
  `secret_key` VARCHAR(64) NOT NULL,
  `is_enabled` TINYINT(1) DEFAULT 0,
  `backup_codes` TEXT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
