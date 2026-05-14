-- Database Migration v10: Monitor Optimization
-- Optimization for historical log viewing (up to 2 years)

-- 1. Index for basic monitoring queries (type filtering)
ALTER TABLE `log` ADD INDEX `idx_log_type` (`type`);

-- 2. Index for chronological retrieval and filtering (critical for 2-year range)
ALTER TABLE `log` ADD INDEX `idx_log_type_create` (`type`, `create_at`);

-- 3. Index for success/failure analysis
ALTER TABLE `log` ADD INDEX `idx_log_type_detail` (`type`, `log_detail`(20));
