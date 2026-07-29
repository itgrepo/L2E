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
