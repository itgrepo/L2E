-- setup_mock_presentation_v2.sql
-- Clear old data to ensure a clean state
DELETE FROM service;

-- 1. Population Data (ข้อมูลประชากร)
INSERT INTO service (service_id, service_name, organization, category, description, status, accessibility, data_format, dataset_id, api_enabled, create_at) 
VALUES (1, 'สถิติจำนวนประชากรแยกตามรายหน้า พ.ศ. 2566', 'กรมการปกครอง', 'ข้อมูลประชากร', 'ข้อมูลจำนวนประชากรรายภาคและรายจังหวัด จำแนกตามช่วงอายุและสัญชาติ เพื่อการวางแผนนโยบาย', 'Active', 'Open Data', 'CSV,API,JSON', 'POP-001', 1, NOW());

INSERT INTO service (service_id, service_name, organization, category, description, status, accessibility, data_format, dataset_id, api_enabled, create_at) 
VALUES (2, 'ข้อมูลทะเบียนราษฎร์และบ้านรายเขต (กรุงเทพฯ)', 'กทม.', 'ข้อมูลประชากร', 'สถิติจำนวนบ้านและประชากรที่มีชื่ออยู่ในทะเบียนบ้านภายในเขตพื้นที่กรุงเทพมหานคร', 'Active', 'Open Data', 'JSON', 'POP-002', 1, NOW());

-- 2. Health Data (สาธารณสุข)
INSERT INTO service (service_id, service_name, organization, category, description, status, accessibility, data_format, dataset_id, api_enabled, create_at) 
VALUES (3, 'สถานะสุขภาพและพฤติกรรมเสี่ยงรายจังหวัด', 'กรมควบคุมโรค', 'สาธารณสุข', 'รวบรวมข้อมูลพฤติกรรมเสี่ยงด้านสุขภาพที่สำคัญของประชาชนในแต่ละจังหวัด', 'Active', 'Restricted', 'CSV,API', 'HEA-001', 1, NOW());

INSERT INTO service (service_id, service_name, organization, category, description, status, accessibility, data_format, dataset_id, api_enabled, create_at) 
VALUES (4, 'จำนวนสถานพยาบาลและเตียงผู้ป่วยรายอำเภอ', 'กระทรวงสาธารณสุข', 'สาธารณสุข', 'ข้อมูลตำแหน่งที่ตั้งและศักยภาพของสถานพยาบาลทั่วประเทศเพื่อการประเมินการเข้าถึงบริการ', 'Active', 'Open Data', 'API,XML', 'HEA-002', 1, NOW());

-- 3. Education Data (การศึกษา)
INSERT INTO service (service_id, service_name, organization, category, description, status, accessibility, data_format, dataset_id, api_enabled, create_at) 
VALUES (5, 'สถิติจำนวนนักเรียนและบุคลากรทางการศึกษา', 'กระทรวงศึกษาธิการ', 'การศึกษา', 'สรุปสถิติจำนวนนักเรียนรายชั้นปีและจำนวนครูแยกตามสังกัดหน่วยงานการศึกษา', 'Active', 'Open Data', 'CSV,XLS', 'EDU-001', 1, NOW());

-- 4. Economy Data (เศรษฐกิจ)
INSERT INTO service (service_id, service_name, organization, category, description, status, accessibility, data_format, dataset_id, api_enabled, create_at) 
VALUES (6, 'ดัชนีราคาผู้บริโภคและอัตราเงินเฟ้อรายเดือน', 'กระทรวงพาณิชย์', 'เศรษฐกิจ', 'รายงานดัชนีราคาผู้บริโภคทั่วไปและอัตราเงินเฟ้อเพื่อใช้เป็นตัวชี้วัดเสถียรภาพทางเศรษฐกิจ', 'Active', 'Open Data', 'API,JSON', 'ECO-001', 1, NOW());

-- Add some logs to make the usage chart look alive
DELETE FROM log;
INSERT INTO log (user_id, log_detail, type, create_at) VALUES (810, 'Accessed Dataset: POP-001', 'API', DATE_SUB(NOW(), INTERVAL 1 DAY));
INSERT INTO log (user_id, log_detail, type, create_at) VALUES (810, 'Accessed Dataset: ECO-001', 'API', DATE_SUB(NOW(), INTERVAL 2 DAY));
INSERT INTO log (user_id, log_detail, type, create_at) VALUES (810, 'Downloaded Dataset: EDU-001', 'Download', DATE_SUB(NOW(), INTERVAL 3 DAY));
INSERT INTO log (user_id, log_detail, type, create_at) VALUES (810, 'Accessed Dataset: HEA-002', 'API', DATE_SUB(NOW(), INTERVAL 4 DAY));
INSERT INTO log (user_id, log_detail, type, create_at) VALUES (810, 'Accessed Dataset: POP-002', 'API', DATE_SUB(NOW(), INTERVAL 5 DAY));
INSERT INTO log (user_id, log_detail, type, create_at) VALUES (810, 'Accessed Dataset: POP-001', 'API', NOW());
INSERT INTO service (
    dataset_id, 
    service_name, 
    description, 
    organization, 
    category, 
    tags, 
    accessibility, 
    license, 
    contact_name, 
    contact_email, 
    update_freq_unit, 
    data_format, 
    status, 
    create_at,
    api_enabled
) VALUES (
    'DS-MSDHS-2026-001',
    'รายงานสถิติข้อมูลคนพิการที่มีบัตรประจำตัวคนพิการทั่วประเทศ',
    'ชุดข้อมูลแสดงจำนวนคนพิการที่ได้รับการออกบัตรประจำตัวคนพิการ จำแนกตามประเภทความพิการ เพศ ช่วงอายุ และระดับการศึกษา ข้อมูลนี้ใช้สำหรับวางแผนนโยบายและจัดสรรงบประมาณการให้ความช่วยเหลือคนพิการ',
    'กรมส่งเสริมและพัฒนาคุณภาพชีวิตคนพิการ (พก.)',
    'สวัสดิการสังคมและสิทธิมนุษยชน',
    'คนพิการ,บัตรคนพิการ,สวัสดิการสังคม,สถิติ',
    'Public',
    'Open Data Common (ODC)',
    'ศูนย์ข้อมูลและสถิติคนพิการ',
    'data@dep.go.th',
    'รายเดือน',
    'CSV,JSON,API',
    'Active',
    NOW(),
    1
);
