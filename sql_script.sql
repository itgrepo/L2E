-- Drop foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- Move existing users
UPDATE user SET previlage_id = 99 WHERE previlage_id = 1;
UPDATE user SET previlage_id = 2 WHERE previlage_id = 3;
UPDATE user SET previlage_id = 4 WHERE previlage_id = 99;

-- Move existing menu permissions
DELETE FROM menu_permission WHERE previlage_id NOT IN (1, 3);
UPDATE menu_permission SET previlage_id = 99 WHERE previlage_id = 1;
UPDATE menu_permission SET previlage_id = 2 WHERE previlage_id = 3;
UPDATE menu_permission SET previlage_id = 4 WHERE previlage_id = 99;

-- Recreate codename_previlage
DELETE FROM codename_previlage;
INSERT INTO codename_previlage (previlage_id, previlage_name) VALUES
(1, 'ผู้ใช้งานภายนอก'),
(2, 'ผู้ใช้งานทั่วไป (ที่ยังไม่ได้รับสิทธิ)'),
(3, 'ผู้ดูแลชุดข้อมูลรายหน่วยงาน'),
(4, 'ผู้ดูแลระบบ'),
(5, 'ผู้ใช้งานภายในที่มีสิทธิใน Dataset');

-- Insert default menu permissions for new roles 1, 3, 5
INSERT IGNORE INTO menu_permission (previlage_id, menu_name_id, value)
SELECT 1, menu_name_id, 'No' FROM menu_name;

INSERT IGNORE INTO menu_permission (previlage_id, menu_name_id, value)
SELECT 3, menu_name_id, 'No' FROM menu_name;

INSERT IGNORE INTO menu_permission (previlage_id, menu_name_id, value)
SELECT 5, menu_name_id, 'No' FROM menu_name;

SET FOREIGN_KEY_CHECKS = 1;
