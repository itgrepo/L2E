CREATE TABLE IF NOT EXISTS `source_system` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `name_th` varchar(255) NOT NULL,
  `name_en` varchar(255) NOT NULL,
  `description` text,
  `active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO `source_system` (`code`, `name_th`, `name_en`) VALUES
('SRC-01', 'ฐานข้อมูลทะเบียนหลักสูตร L2E', 'L2E Course Registration Database'),
('SRC-02', 'ระบบบันทึกผลการเรียน L2E', 'L2E Learning Record System'),
('SRC-03', 'ระบบประเมินสมรรถนะ L2E', 'L2E Competency Assessment System'),
('SRC-04', 'ระบบตลาดแรงงานและจัดหางาน L2E', 'L2E Labour Market and Job System'),
('SRC-05', 'ระบบวิเคราะห์ความฉลาดทางทักษะ L2E', 'L2E Skill Analytics System');

DELIMITER $$
CREATE PROCEDURE MigrateSourceSystem()
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'service' 
        AND COLUMN_NAME = 'source_system_id'
    ) THEN
        ALTER TABLE `service` ADD COLUMN `source_system_id` int(11) DEFAULT NULL AFTER `data_source`;
        ALTER TABLE `service` ADD CONSTRAINT `fk_service_source_system` FOREIGN KEY (`source_system_id`) REFERENCES `source_system` (`id`) ON DELETE SET NULL;
        
        -- Migrate distinct values to exact matches
        UPDATE `service` s
        JOIN `source_system` ss ON s.data_source = ss.name_th
        SET s.source_system_id = ss.id
        WHERE s.data_source IS NOT NULL AND s.data_source != '';
    END IF;
END $$
DELIMITER ;

CALL MigrateSourceSystem();
DROP PROCEDURE MigrateSourceSystem;
