-- Drop and recreate 'log' table to match the INSERT statement in logAction()
DROP TABLE IF EXISTS `log`;
CREATE TABLE `log` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `ip` varchar(255) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  `log_detail` text,
  `type` varchar(255) DEFAULT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `country` varchar(255) DEFAULT 'None',
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
