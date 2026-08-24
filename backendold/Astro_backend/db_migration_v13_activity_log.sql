-- Add device column to log table to track User-Agent
ALTER TABLE `log` ADD COLUMN `device` VARCHAR(255) DEFAULT 'Unknown';
