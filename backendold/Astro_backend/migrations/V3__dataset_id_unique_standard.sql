-- Fix empty dataset_ids
UPDATE `service` 
SET `dataset_id` = CONCAT('LEGACY_', `service_id`) 
WHERE `dataset_id` IS NULL OR `dataset_id` = '';

-- Make sure no duplicate dataset_id exists
-- If there are duplicates, we would append _1, _2 etc, but we verified there are none.

DELIMITER $$
CREATE PROCEDURE AddUniqueConstraintIfNotExists()
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM INFORMATION_SCHEMA.STATISTICS 
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'service' 
        AND INDEX_NAME = 'idx_dataset_id_unique'
    ) THEN
        ALTER TABLE `service` ADD UNIQUE INDEX `idx_dataset_id_unique` (`dataset_id`);
    END IF;
END $$
DELIMITER ;

CALL AddUniqueConstraintIfNotExists();
DROP PROCEDURE AddUniqueConstraintIfNotExists;
