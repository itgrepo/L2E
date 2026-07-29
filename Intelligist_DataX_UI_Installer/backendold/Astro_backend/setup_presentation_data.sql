

-- 1. Create a professional mock table with realistic data
CREATE TABLE IF NOT EXISTS mock_population (
    id INT AUTO_INCREMENT PRIMARY KEY,
    province VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    total_population INT,
    male_population INT,
    female_population INT,
    data_year INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

TRUNCATE TABLE mock_population;

INSERT INTO mock_population (province, region, total_population, male_population, female_population, data_year) VALUES
('กรุงเทพมหานคร', 'ภาคกลาง', 5494932, 2588320, 2906612, 2023),
('เชียงใหม่', 'ภาคเหนือ', 1789385, 863212, 926173, 2023),
('ภูเก็ต', 'ภาคใต้', 418785, 198218, 220567, 2023),
('ขอนแก่น', 'ภาคตะวันออกเฉียงเหนือ', 1792404, 878342, 914062, 2023),
('ชลบุรี', 'ภาคตะวันออก', 1583672, 770110, 813562, 2023);

-- 2. Clean up any previous presentation data
DELETE FROM service WHERE dataset_id = 'P_2023';

-- 3. Register it in the API Gateway 'service' table
INSERT INTO service (
    service_name, dataset_id, category, description, 
    api_enabled, api_type, api_db_name, api_source_type, api_source_name,
    api_request_fields, api_response_fields, organization, status
) VALUES (
    'สถิติประชากรรายจังหวัด ปี 2566', 'P_2023', 'สถิติประชากร', 
    'ข้อมูลสถิติจำนวนประชากรแยกตามจังหวัดและเพศ เพื่อการวิเคราะห์แนวโน้มประชากร',
    1, 'scope', 'psu_backend', 'table', 'mock_population',
    '["province", "region"]', '["province", "region", "total_population", "male_population", "female_population"]',
    'ศูนย์เทคโนโลยีสารสนเทศ (IT Center)', 'Active'
);

SET @demo_svc_id = LAST_INSERT_ID();

-- 4. Create Mock Users
INSERT IGNORE INTO user (user_id, username, password, firstname, lastname) VALUES 
(801, 'bkk_admin', '1234', 'สมชาย', 'ใจดี'),
(802, 'cnx_admin', '1234', 'สมหญิง', 'เชียงใหม่'),
(803, 'temp_user', '1234', 'นักวิจัย', 'อิสระ');

-- Clean up existing keys for these users on this service
DELETE FROM api_credentials WHERE service_id = @demo_svc_id;

-- 5. Generate API Keys with Scopes

-- Key: BKK Admin (Valid, Scoped to 'กรุงเทพมหานคร')
INSERT INTO api_credentials (service_id, user_id, secret_key, status, expires_at) 
VALUES (@demo_svc_id, 801, 'DEMO_KEY_BKK_999', 'active', '2026-12-31 23:59:59');
SET @cred_bkk = LAST_INSERT_ID();

INSERT INTO api_scopes (credential_id, scope_json) 
VALUES (@cred_bkk, '{"province": ["กรุงเทพมหานคร"]}');

-- Key: CNX Admin (Valid, Scoped to 'เชียงใหม่' และภาคเหนือทั้งหมด)
INSERT INTO api_credentials (service_id, user_id, secret_key, status, expires_at) 
VALUES (@demo_svc_id, 802, 'DEMO_KEY_CNX_555', 'active', '2026-12-31 23:59:59');
SET @cred_cnx = LAST_INSERT_ID();

INSERT INTO api_scopes (credential_id, scope_json) 
VALUES (@cred_cnx, '{"region": ["ภาคเหนือ"]}');

-- Key: Temp Researcher (Expired Key)
INSERT INTO api_credentials (service_id, user_id, secret_key, status, expires_at) 
VALUES (@demo_svc_id, 803, 'DEMO_KEY_EXPIRED', 'active', '2023-01-01 00:00:00');

-- 6. Inject beautiful Mock Logs for Dashboard to look active
INSERT INTO log (user_id, log_detail, type, path, ip, country) VALUES
(801, '[200] API Invoked Successfully', 'API', '/dataapi/api/v1/P_2023', '10.0.1.5', 'Thailand'),
(801, '[200] API Invoked Successfully', 'API', '/dataapi/api/v1/P_2023', '10.0.1.5', 'Thailand'),
(802, '[200] API Invoked Successfully', 'API', '/dataapi/api/v1/P_2023', '110.78.210.12', 'Thailand'),
(803, '[403] API Key has expired', 'API', '/dataapi/api/v1/P_2023', '192.168.1.100', 'Unknown'),
(0, '[403] Invalid API Key or Dataset ID', 'API', '/dataapi/api/v1/P_2023', '52.4.99.1', 'USA'),
(802, '[200] API Invoked Successfully', 'API', '/dataapi/api/v1/P_2023', '110.78.210.12', 'Thailand');
