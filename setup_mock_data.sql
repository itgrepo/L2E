CREATE TABLE IF NOT EXISTS mock_pop_001 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    province VARCHAR(100),
    population_male INT,
    population_female INT,
    total_population INT,
    year_recorded VARCHAR(4)
);

TRUNCATE TABLE mock_pop_001;

INSERT INTO mock_pop_001 (province, population_male, population_female, total_population, year_recorded) VALUES
('Bangkok', 2500000, 2700000, 5200000, '2566'),
('Chiang Mai', 800000, 850000, 1650000, '2566'),
('Phuket', 200000, 220000, 420000, '2566'),
('Khon Kaen', 900000, 950000, 1850000, '2566'),
('Chon Buri', 700000, 750000, 1450000, '2566');

UPDATE service 
SET api_db_name = DATABASE(), 
    api_source_name = 'mock_pop_001' 
WHERE dataset_id = 'POP-001';
