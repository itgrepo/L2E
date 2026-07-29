-- 1. Extend 'user' table
ALTER TABLE `user` 
ADD COLUMN `national_id` varchar(255) DEFAULT NULL,
ADD COLUMN `national_id_book` varchar(255) DEFAULT NULL,
ADD COLUMN `national_id_mode` int(11) DEFAULT NULL,
ADD COLUMN `policy_id` int(11) DEFAULT NULL,
ADD COLUMN `usage_objective` text DEFAULT NULL,
ADD COLUMN `other_object` text DEFAULT NULL,
ADD COLUMN `count_login` int(11) DEFAULT 0,
ADD COLUMN `2fa_status` varchar(255) DEFAULT 'off',
ADD COLUMN `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 2. Create 'user_activity' table
CREATE TABLE IF NOT EXISTS `user_activity` (
  `activity_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `login_status` varchar(255) DEFAULT '0',
  `login_respond` bigint(20) DEFAULT 0,
  `create_date` bigint(20) DEFAULT 0,
  `status_account` varchar(255) DEFAULT '1',
  `password` varchar(255) DEFAULT NULL,
  `emailnews` varchar(255) DEFAULT '-',
  PRIMARY KEY (`activity_id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 3. Create 'DataField' table
CREATE TABLE IF NOT EXISTS `DataField` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `national_id` varchar(255) DEFAULT NULL,
  `national_id_book` varchar(255) DEFAULT NULL,
  `sublevel_id` float DEFAULT NULL,
  `expiration` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 4. Create 'sublevel_master' table
CREATE TABLE IF NOT EXISTS `sublevel_master` (
  `sublevel_id` float NOT NULL,
  `Level_Master_id` int(11) NOT NULL,
  PRIMARY KEY (`sublevel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 5. Create 'codename_policy' table
CREATE TABLE IF NOT EXISTS `codename_policy` (
  `policy_id` int(11) NOT NULL AUTO_INCREMENT,
  `policy_name` varchar(255) NOT NULL,
  PRIMARY KEY (`policy_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 6. Create 'user_password_history' table
CREATE TABLE IF NOT EXISTS `user_password_history` (
  `history_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `password_rank` int(11) DEFAULT 1,
  `password` varchar(255) NOT NULL,
  `create_at` bigint(20) NOT NULL,
  PRIMARY KEY (`history_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 7. Create 'timetable_activity' table
CREATE TABLE IF NOT EXISTS `timetable_activity` (
  `activity_desc` varchar(255) NOT NULL,
  `duration` int(11) NOT NULL,
  PRIMARY KEY (`activity_desc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 8. Create 'service' table (Catalog)
CREATE TABLE IF NOT EXISTS `service` (
  `service_id` int(11) NOT NULL AUTO_INCREMENT,
  `service_name` varchar(255) NOT NULL,
  `description` text,
  `access_type` varchar(255) DEFAULT 'Public',
  `status` varchar(255) DEFAULT 'Active',
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 9. Update 'log' table
ALTER TABLE `log`
ADD COLUMN `ip` varchar(255) DEFAULT NULL,
ADD COLUMN `path` varchar(255) DEFAULT NULL,
ADD COLUMN `type` varchar(255) DEFAULT NULL,
ADD COLUMN `country` varchar(255) DEFAULT 'None';

-- Default Master Data
INSERT INTO `codename_policy` (`policy_id`, `policy_name`) VALUES (1, 'Default Policy');
INSERT INTO `sublevel_master` (`sublevel_id`, `Level_Master_id`) VALUES (1, 1), (1.1, 1), (1.2, 1);
INSERT INTO `timetable_activity` (`activity_desc`, `duration`) VALUES ('ForceChangePassword', 90);
