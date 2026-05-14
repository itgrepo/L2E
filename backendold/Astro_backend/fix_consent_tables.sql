-- 1. Create 'consent_agreement' table
CREATE TABLE IF NOT EXISTS `consent_agreement` (
  `consent_agreement_id` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` varchar(255) DEFAULT NULL,
  `version` int(11) DEFAULT 1,
  `status` varchar(255) DEFAULT 'inactive',
  `consent_file` longblob DEFAULT NULL,
  `consent_text` text DEFAULT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`consent_agreement_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 2. Create 'user_agreement' table
CREATE TABLE IF NOT EXISTS `user_agreement` (
  `user_id` int(11) NOT NULL,
  `ip` varchar(255) DEFAULT NULL,
  `consent_agreement_id` int(11) NOT NULL,
  `date_time` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`user_id`, `consent_agreement_id`),
  KEY `consent_agreement_id` (`consent_agreement_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 3. Create 'AcceptCookie' table
CREATE TABLE IF NOT EXISTS `AcceptCookie` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `browsers_name` varchar(255) DEFAULT NULL,
  `browsers_version` varchar(255) DEFAULT NULL,
  `ip` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT 'None',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Insert a default active consent to satisfy the login check
INSERT INTO `consent_agreement` (`file_name`, `version`, `status`, `consent_text`) 
VALUES ('Standard Terms v1', 1, 'active', 'Terms and conditions for Data Exchange Platform.');

-- Pre-accept for testadmin to avoid redirection loop in test environment
INSERT INTO `user_agreement` (`user_id`, `ip`, `consent_agreement_id`, `date_time`)
SELECT user_id, '127.0.0.1', (SELECT consent_agreement_id FROM consent_agreement WHERE status = 'active'), UNIX_TIMESTAMP()
FROM user WHERE username = 'testadmin';
