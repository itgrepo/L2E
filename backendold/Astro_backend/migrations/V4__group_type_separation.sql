-- Migration V4: Separate User Groups from Dataset Groups
-- Date: 2026-10-14

-- 1. Add group_type column to group_user
ALTER TABLE `group_user` ADD COLUMN IF NOT EXISTS `group_type` VARCHAR(50) NOT NULL DEFAULT 'user_group' AFTER `group_name`;

-- 2. Mark existing dataset groups
UPDATE `group_user` SET `group_type` = 'dataset_group' WHERE `group_id` IN (11, 12, 13, 14);

-- 3. Create initial standard user groups
INSERT INTO `group_user` (`group_name`, `group_type`, `create_at`) 
SELECT 'กลุ่มผู้ใช้งานทั่วไป', 'user_group', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `group_user` WHERE `group_name` = 'กลุ่มผู้ใช้งานทั่วไป' AND `group_type` = 'user_group');

INSERT INTO `group_user` (`group_name`, `group_type`, `create_at`) 
SELECT 'กลุ่มเจ้าหน้าที่ BDE', 'user_group', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `group_user` WHERE `group_name` = 'กลุ่มเจ้าหน้าที่ BDE' AND `group_type` = 'user_group');

INSERT INTO `group_user` (`group_name`, `group_type`, `create_at`) 
SELECT 'กลุ่มเจ้าหน้าที่ ThaiMOOC', 'user_group', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `group_user` WHERE `group_name` = 'กลุ่มเจ้าหน้าที่ ThaiMOOC' AND `group_type` = 'user_group');

INSERT INTO `group_user` (`group_name`, `group_type`, `create_at`) 
SELECT 'กลุ่มเจ้าหน้าที่ TPQI', 'user_group', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `group_user` WHERE `group_name` = 'กลุ่มเจ้าหน้าที่ TPQI' AND `group_type` = 'user_group');

INSERT INTO `group_user` (`group_name`, `group_type`, `create_at`) 
SELECT 'กลุ่มผู้บริหารและวิเคราะห์ข้อมูล', 'user_group', NOW()
WHERE NOT EXISTS (SELECT 1 FROM `group_user` WHERE `group_name` = 'กลุ่มผู้บริหารและวิเคราะห์ข้อมูล' AND `group_type` = 'user_group');

-- 4. Clean up dataset groups from service_group_access
DELETE FROM `service_group_access` WHERE `group_id` IN (11, 12, 13, 14);
