CREATE TABLE IF NOT EXISTS `l2e_dataset_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `name_th` varchar(255) NOT NULL,
  `name_en` varchar(255) NOT NULL,
  `prefix` varchar(10) NOT NULL,
  `active` tinyint(1) DEFAULT 1,
  `display_order` int(11) DEFAULT 0,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_code` (`code`),
  UNIQUE KEY `idx_prefix` (`prefix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO `l2e_dataset_group` (`code`, `name_th`, `name_en`, `prefix`, `display_order`) VALUES
('course', 'Course', 'Course', 'CRS-', 1),
('completion', 'Completion', 'Completion', 'CMP-', 2),
('competency', 'Competency', 'Competency', 'COM-', 3),
('job_market', 'Job / Labour Market', 'Job / Labour Market', 'JOB-', 4),
('skill_analytics', 'Skill Analytics', 'Skill Analytics', 'SKL-', 5);

DELIMITER $$
CREATE PROCEDURE AddGroupColumnIfNotExists()
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'service' 
        AND COLUMN_NAME = 'l2e_group_id'
    ) THEN
        ALTER TABLE `service` ADD COLUMN `l2e_group_id` int(11) DEFAULT NULL AFTER `dataset_id`;
        ALTER TABLE `service` ADD CONSTRAINT `fk_service_l2e_group` FOREIGN KEY (`l2e_group_id`) REFERENCES `l2e_dataset_group` (`id`) ON DELETE SET NULL;
    END IF;
END $$
DELIMITER ;

CALL AddGroupColumnIfNotExists();
DROP PROCEDURE AddGroupColumnIfNotExists;
