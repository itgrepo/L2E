CREATE TABLE IF NOT EXISTS `organization_role_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `name_th` varchar(255) NOT NULL,
  `name_en` varchar(255) NOT NULL,
  `active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO `organization_role_master` (`code`, `name_th`, `name_en`) VALUES
('PROVIDER', 'ผู้ให้บริการข้อมูล', 'Data Provider'),
('EMPLOYER', 'นายจ้าง/ผู้ใช้งานข้อมูล', 'Employer'),
('SOURCE_OWNER', 'เจ้าของระบบต้นทาง', 'Source Owner'),
('PLATFORM_OWNER', 'เจ้าของแพลตฟอร์ม', 'Platform Owner'),
('REGULATOR', 'ผู้กำกับดูแล', 'Regulator');

CREATE TABLE IF NOT EXISTS `organization_role_mapping` (
  `organization_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`organization_id`, `role_id`),
  CONSTRAINT `fk_org_role_org` FOREIGN KEY (`organization_id`) REFERENCES `organization` (`org_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_org_role_role` FOREIGN KEY (`role_id`) REFERENCES `organization_role_master` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DELIMITER $$
CREATE PROCEDURE ExtendOrganization()
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'organization' 
        AND COLUMN_NAME = 'contact_name'
    ) THEN
        ALTER TABLE `organization` 
        ADD COLUMN `contact_name` varchar(255) DEFAULT NULL,
        ADD COLUMN `contact_email` varchar(255) DEFAULT NULL,
        ADD COLUMN `contact_phone` varchar(50) DEFAULT NULL,
        ADD COLUMN `is_active` tinyint(1) DEFAULT 1;
    END IF;
END $$
DELIMITER ;

CALL ExtendOrganization();
DROP PROCEDURE ExtendOrganization;
