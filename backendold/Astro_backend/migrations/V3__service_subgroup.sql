-- V3: Add subgroup and subgroup_id columns to service table
ALTER TABLE `service` ADD COLUMN IF NOT EXISTS `subgroup` VARCHAR(100) DEFAULT NULL AFTER `l2e_group_id`;
ALTER TABLE `service` ADD COLUMN IF NOT EXISTS `subgroup_id` INT(11) DEFAULT NULL AFTER `subgroup`;

UPDATE `service` SET `subgroup` = 'course', `subgroup_id` = 1 
WHERE `dataset_id` LIKE '%CRS%' OR `category` = 'Course Data' OR `category` = 'Learning Catalog';
