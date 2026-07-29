-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: node1
-- Generation Time: May 28, 2019 at 08:52 AM
-- Server version: 10.1.23-MariaDB-1~jessie
-- PHP Version: 7.2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `intelligist_set_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `category`
--

CREATE TABLE `category` (
  `category_id` int(11) NOT NULL,
  `category_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `category`
--

INSERT INTO `category` (`category_id`, `category_name`) VALUES
(1, 'Resource'),
(2, 'Financial');

-- --------------------------------------------------------

--
-- Table structure for table `codename_download_type`
--

CREATE TABLE `codename_download_type` (
  `download_type_id` int(11) NOT NULL,
  `download_type_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `codename_download_type`
--

INSERT INTO `codename_download_type` (`download_type_id`, `download_type_name`) VALUES
(1, 'WEB Page'),
(2, 'Excel File'),
(3, 'CSV File'),
(4, 'Text File'),
(5, 'XML File'),
(6, 'Link Web Excel'),
(7, 'Link Web CSV'),
(8, 'Web Scraping'),
(9, 'API'),
(10, 'SOAP');

-- --------------------------------------------------------

--
-- Table structure for table `codename_group_permission`
--

CREATE TABLE `codename_group_permission` (
  `group_permission_id` int(11) NOT NULL,
  `group_permission_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `codename_import_status`
--

CREATE TABLE `codename_import_status` (
  `import_status_id` int(11) NOT NULL,
  `import_status_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `codename_import_status`
--

INSERT INTO `codename_import_status` (`import_status_id`, `import_status_name`) VALUES
(1, 'Error'),
(2, 'Pending'),
(3, 'Complete');

-- --------------------------------------------------------

--
-- Table structure for table `codename_metadata_status`
--

CREATE TABLE `codename_metadata_status` (
  `metadata_status_id` int(11) NOT NULL,
  `metadata_status_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `codename_metadata_status`
--

INSERT INTO `codename_metadata_status` (`metadata_status_id`, `metadata_status_name`) VALUES
(1, 'Inactive'),
(2, 'Active');

-- --------------------------------------------------------

--
-- Table structure for table `codename_mode_viewer`
--

CREATE TABLE `codename_mode_viewer` (
  `mode_viewer_id` int(11) NOT NULL,
  `mode_viewer_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `codename_mode_viewer`
--

INSERT INTO `codename_mode_viewer` (`mode_viewer_id`, `mode_viewer_name`) VALUES
(1, 'Public'),
(2, 'Private');

-- --------------------------------------------------------

--
-- Table structure for table `codename_previlage`
--

CREATE TABLE `codename_previlage` (
  `previlage_id` int(11) NOT NULL,
  `previlage_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `codename_previlage`
--

INSERT INTO `codename_previlage` (`previlage_id`, `previlage_name`) VALUES
(1, 'RootAdmin'),
(2, 'Admin'),
(3, 'User');

-- --------------------------------------------------------

--
-- Table structure for table `codename_schedule_mode`
--

CREATE TABLE `codename_schedule_mode` (
  `schedule_mode_id` int(11) NOT NULL,
  `schedule_mode_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `codename_schedule_mode`
--

INSERT INTO `codename_schedule_mode` (`schedule_mode_id`, `schedule_mode_name`) VALUES
(1, 'None'),
(2, 'Daily'),
(3, 'Day Of Month'),
(4, 'End Of Month'),
(5, 'First day of the month');

-- --------------------------------------------------------

--
-- Table structure for table `codename_status`
--

CREATE TABLE `codename_status` (
  `status_id` int(11) NOT NULL,
  `status_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `codename_status`
--

INSERT INTO `codename_status` (`status_id`, `status_name`) VALUES
(1, 'Offline'),
(2, 'Online'),
(3, 'Suspended'),
(4, 'Pending'),
(5, 'New');

-- --------------------------------------------------------

--
-- Table structure for table `export_excel`
--

CREATE TABLE `export_excel` (
  `export_excel_id` int(11) NOT NULL,
  `export_excel_name` text NOT NULL,
  `frequency` varchar(255) NOT NULL,
  `source_id` varchar(255) NOT NULL,
  `category_id` int(11) NOT NULL,
  `sub_category_id` int(11) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `mongo_file_id_excel` varchar(255) NOT NULL,
  `mongo_file_id_csv` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `trans_date` datetime NOT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `export_excel`
--

INSERT INTO `export_excel` (`export_excel_id`, `export_excel_name`, `frequency`, `source_id`, `category_id`, `sub_category_id`, `file_name`, `mongo_file_id_excel`, `mongo_file_id_csv`, `user_id`, `trans_date`, `create_at`) VALUES
(1, 'test_list_detail', '', 'TDWF001', 0, 0, '', '0', '0', 1, '0000-00-00 00:00:00', '2019-05-26 14:49:52'),
(3, 'test001', '', 'TDWF000101', 0, 0, '', '12345', '67890', 1, '2019-05-26 17:42:14', '2019-05-26 16:38:49'),
(4, 'test001', '', 'TDWF000101', 0, 0, '', '12345', '67890', 1, '2019-05-27 00:45:02', '2019-05-28 06:28:41'),
(5, 'Quantity of Commercial Primary Energy Production, Classified by Energy Type and Source (Unit: Original Unit)', 'Monthly', 'DWF000101', 1, 1, '1.1-2_Production(original ALL)', '5cead285832ca243a251e0e0', '5ceadf7ad3bdeeb930f61c74', 1, '2019-05-27 00:00:00', '2019-05-28 08:18:44'),
(6, 'Quantity of Commercial Primary Energy Production, Classified by Energy Type and Source (Unit: BBL/Day - Crude Oil Equivalent)', 'Monthly', 'DWF000501', 1, 1, '1.1-3_Production(BBL DAY)', '5ceadfe2d3bdeeb930f61c78', '5ceae005d3bdeeb930f61c7a', 1, '2019-05-27 00:00:00', '2019-05-28 08:19:00'),
(7, 'Quantity of Commercial Primary Energy Production, Classified by Energy Type and Source (Unit: KTOE)', 'Monthly', 'DWF000901', 1, 1, '1.1-4_Production(KTOE)', '5ceae1ebd3bdeeb930f61c7d', '5ceae218d3bdeeb930f61c7f', 1, '2019-05-27 00:00:00', '2019-05-28 08:19:03'),
(8, 'Quantity of Energy Reserves, Classified by Energy Type', 'Yearly', 'DWF001301', 1, 1, 'Quantity_of_Energy_Reserves,_Classified_by_Energy_Type', '5ceae227d3bdeeb930f61c81', '5ceae235d3bdeeb930f61c83', 1, '2019-05-27 00:00:00', '2019-05-28 08:20:11'),
(9, 'Quantity of Energy Supply in Thailand, Classified by Energy Type (Unit: Orginal Unit; BBL/Day-Crude Oil Equivalent)', 'Monthly', 'DWF001401', 1, 1, 'S1_DMF 996_Supply', '5ceae247d3bdeeb930f61c85', '5ceae260d3bdeeb930f61c87', 1, '2019-05-27 00:00:00', '2019-05-28 08:20:50'),
(10, 'Actual and Forecast of World Petroleum and Other Liquids Production (Unit: Million BBL/Day)', 'Monthly', 'DWF002701', 1, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:22:02'),
(11, 'Actual and Forecast of U.S. Crude Oil Production (Unit: Million BBL/Day)', 'Monthly', 'DWF002801', 1, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:23:08'),
(12, 'Crude Palm Oil Production and Price in Southern Region (Unit: Metric Tons, Baht/KG.)', 'Monthly', 'DWF002901', 1, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:24:05'),
(13, 'Quantity of Mineral Production, Classified by Mineral Type (Unit: Ton)', 'Yearly', 'DWF003001', 1, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:24:46'),
(14, 'Volume of Fuel Service of Suvarnabhumi Airport and Donmueng Airport (Unit: Million Litres)', 'Monthly', 'DWF003101', 1, 2, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:25:20'),
(15, 'Number of Registered Vehicles, Classified by Fuel Type (Unit: Unit)', 'Monthly', 'DWF003201', 1, 2, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:25:30'),
(16, 'Number of New Registered Vehicles, Classified by Fuel Type (Unit: Unit)', 'Monthly', 'DWF003301', 1, 2, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:25:42'),
(17, 'Actual and Forecast of World Petroleum and Other Liquids Consumption (Unit: Million BBL/Day)', 'Monthly', 'DWF003401', 1, 2, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:28:27'),
(18, 'Monthly Energy Prices', 'Monthly', 'DWF003501', 1, 3, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:28:47'),
(19, 'WTI Crude Oil Futures Price (Cushing, OK Crude Oil Futures Contract 1) (Unit: Dollars per Barrel)', 'Daily', 'DWF003601', 1, 3, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:29:30'),
(20, 'Natural Gas Futures Price (Unit: Dollars per Barrel)', 'Daily', 'DWF003701', 1, 3, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:29:51'),
(21, 'All Commercial Banks\' Deposits Classified by Types of Depositors and Accounts (Unit: Millions of Baht)', 'Monthly', 'DWF004701', 2, 2, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:30:27'),
(22, 'Commercial Bank Deposits Outstandings and Withdrawal (Unit: Millions of Baht)', 'Monthly', 'DWF005101', 2, 2, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:32:13'),
(23, 'Weighted Average Deposit Interest Rate of Commercial Banks (Unit: Percent)', 'Quarterly', 'DWF005501', 2, 2, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:32:40'),
(24, 'All Commercial Banks\' Credits Classified by Types of Debtors and Credits (Unit : Millions of Baht)', 'Monthly', 'DWF005801', 2, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:33:07'),
(25, 'Commercial Banks\' Loans, Deposits and Loan to Deposit Ratio (Unit: Millions of Baht)', 'Monthly', 'DWF006201', 2, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:33:37'),
(26, 'Loans to Household and Household Debt to GDP (Unit: Millions of Baht)', 'Quarterly', 'DWF006601', 2, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:34:08'),
(27, 'Number of Plastic Cards (Unit: Cards)', 'Monthly', 'DWF007301', 2, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:35:25'),
(28, 'Nano Finance under Supervision (Unit: Millions of Baht)', 'Monthly', 'DWF008001', 2, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:35:59'),
(29, 'Private Consumption Index and Components (Unit: Points)', 'Monthly', 'DWF008401', 2, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:38:41'),
(30, 'Private Consumption Index and Components (Seasonally Adjusted) (Unit: Points)', 'Monthly', 'DWF008801', 2, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:38:59'),
(31, 'Personal Loan under Supervision (Unit: Millions of Baht)', 'Monthly', 'DWF009201', 2, 1, '', '', '', 1, '2019-05-27 00:00:00', '2019-05-28 08:39:47');

-- --------------------------------------------------------

--
-- Table structure for table `export_metadata`
--

CREATE TABLE `export_metadata` (
  `export_metadata_id` int(11) NOT NULL,
  `export_metadata_name` text NOT NULL,
  `source_id` varchar(255) NOT NULL,
  `category_id` int(11) NOT NULL,
  `sub_category_id` int(11) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `mongo_file_id_metadata` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `trans_date` datetime NOT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `export_metadata`
--

INSERT INTO `export_metadata` (`export_metadata_id`, `export_metadata_name`, `source_id`, `category_id`, `sub_category_id`, `file_name`, `mongo_file_id_metadata`, `user_id`, `trans_date`, `create_at`) VALUES
(1, 'test001', '', 0, 0, '', '12345', 1, '2019-05-27 00:45:02', '2019-05-26 19:07:11'),
(2, 'metadata_ProductionOriginal_ALL', '', 1, 1, 'metadata_ProductionOriginal_ALL', '5ceae293d3bdeeb930f61c89', 1, '2019-05-27 00:00:00', '2019-05-27 06:00:48');

-- --------------------------------------------------------

--
-- Table structure for table `group_permission_detail`
--

CREATE TABLE `group_permission_detail` (
  `group_permission_detail_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `group_permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `group_user`
--

CREATE TABLE `group_user` (
  `group_id` int(11) NOT NULL,
  `group_name` varchar(255) NOT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `group_user_detail`
--

CREATE TABLE `group_user_detail` (
  `group_user_detail_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `log_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `log_detail` text NOT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `metadata`
--

CREATE TABLE `metadata` (
  `metadata_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `source_id` varchar(255) NOT NULL,
  `source_name` varchar(255) NOT NULL,
  `download_type_id` int(11) NOT NULL,
  `status` varchar(255) NOT NULL,
  `web_address` text NOT NULL,
  `mongo_file_id` varchar(255) NOT NULL,
  `localpath` text NOT NULL,
  `header_file` text NOT NULL,
  `append_mode` varchar(255) NOT NULL,
  `ref` varchar(255) NOT NULL,
  `schedule_mode_id` varchar(255) NOT NULL,
  `schedule_status` varchar(255) NOT NULL,
  `schedule_date` varchar(255) NOT NULL,
  `schedule_days` varchar(255) NOT NULL,
  `schedule_month` varchar(255) NOT NULL,
  `schedule_time` varchar(255) NOT NULL,
  `auto_approve` varchar(255) NOT NULL,
  `auto_generate` varchar(255) NOT NULL,
  `mode_viewer_id` int(11) NOT NULL,
  `import_status_id` int(11) NOT NULL,
  `log_message` text NOT NULL,
  `trans_date` datetime NOT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `metadata`
--

INSERT INTO `metadata` (`metadata_id`, `user_id`, `source_id`, `source_name`, `download_type_id`, `status`, `web_address`, `mongo_file_id`, `localpath`, `header_file`, `append_mode`, `ref`, `schedule_mode_id`, `schedule_status`, `schedule_date`, `schedule_days`, `schedule_month`, `schedule_time`, `auto_approve`, `auto_generate`, `mode_viewer_id`, `import_status_id`, `log_message`, `trans_date`, `create_at`) VALUES
(1, 1, 'AA000101', 'test2', 6, '1', '', '', 'test.xml', 'test.xml', '1', '', '1', '0', '', '', '', '', '1', '0', 1, 2, '', '2019-05-24 00:18:50', '2019-05-23 17:18:50'),
(2, 1, 'AA000201', 'test3', 6, '1', '', '1234', 'test.xml', 'test.xml', '1', '', '1', '0', '', '', '', '', '1', '0', 1, 2, '', '2019-05-24 17:17:29', '2019-05-24 10:17:29');

-- --------------------------------------------------------

--
-- Table structure for table `metadata_permission`
--

CREATE TABLE `metadata_permission` (
  `metadata_permission_id` int(11) NOT NULL,
  `metadata_id` int(11) NOT NULL,
  `group_permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sub_category`
--

CREATE TABLE `sub_category` (
  `sub_category_id` int(11) NOT NULL,
  `sub_category_name` varchar(255) NOT NULL,
  `category_id` int(11) NOT NULL,
  `metadata_id` int(11) NOT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `sub_category`
--

INSERT INTO `sub_category` (`sub_category_id`, `sub_category_name`, `category_id`, `metadata_id`, `create_at`) VALUES
(1, 'Supply', 1, 0, '2019-05-26 16:35:50'),
(2, 'Demand', 1, 0, '2019-05-26 16:35:50'),
(3, 'Price', 1, 0, '2019-05-26 16:35:50'),
(4, 'Lending', 2, 0, '2019-05-26 16:35:50'),
(5, 'Deposit', 2, 0, '2019-05-26 16:35:50');

-- --------------------------------------------------------

--
-- Table structure for table `token_register`
--

CREATE TABLE `token_register` (
  `token_id` int(11) NOT NULL,
  `token` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `status` varchar(255) NOT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `token_register`
--

INSERT INTO `token_register` (`token_id`, `token`, `username`, `email`, `status`, `create_at`) VALUES
(1, '451ab3bbbb5743e385f140ccf5c849e6783b83847eda11e9843a0242ac120002', 'user01', 'test@mailmanet.com', 'inactive', '2019-05-25 10:53:03');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `user_id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `firstname` varchar(255) NOT NULL,
  `lastname` varchar(255) NOT NULL,
  `job_title` varchar(255) NOT NULL,
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `previlage_id` int(3) NOT NULL,
  `status_id` int(3) NOT NULL,
  `status_account` varchar(255) NOT NULL,
  `last_update` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`user_id`, `username`, `password`, `email`, `firstname`, `lastname`, `job_title`, `create_at`, `previlage_id`, `status_id`, `status_account`, `last_update`) VALUES
(1, 'admin', '8C6976E5B5410415BDE908BD4DEE15DFB167A9C873FC4BB8A81F6F2AB448A918', 'admin@mailtestintelligist.co.th', 'admin', 'admin', 'admin', '2019-05-25 11:02:29', 1, 2, 'active', '2019-05-19 17:00:00'),
(2, 'user01', 'AAD415A73C4CEF1EF94A5C00B2642B571A3E5494536328AD960DB61889BD9368', 'test@mailmanet.com', 'user01', 'user01', '', '2019-05-25 10:53:03', 3, 1, 'active', '2019-05-25 10:47:19');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `category`
--
ALTER TABLE `category`
  ADD PRIMARY KEY (`category_id`);

--
-- Indexes for table `codename_download_type`
--
ALTER TABLE `codename_download_type`
  ADD PRIMARY KEY (`download_type_id`);

--
-- Indexes for table `codename_group_permission`
--
ALTER TABLE `codename_group_permission`
  ADD PRIMARY KEY (`group_permission_id`);

--
-- Indexes for table `codename_import_status`
--
ALTER TABLE `codename_import_status`
  ADD PRIMARY KEY (`import_status_id`);

--
-- Indexes for table `codename_metadata_status`
--
ALTER TABLE `codename_metadata_status`
  ADD PRIMARY KEY (`metadata_status_id`);

--
-- Indexes for table `codename_mode_viewer`
--
ALTER TABLE `codename_mode_viewer`
  ADD PRIMARY KEY (`mode_viewer_id`);

--
-- Indexes for table `codename_previlage`
--
ALTER TABLE `codename_previlage`
  ADD PRIMARY KEY (`previlage_id`);

--
-- Indexes for table `codename_schedule_mode`
--
ALTER TABLE `codename_schedule_mode`
  ADD PRIMARY KEY (`schedule_mode_id`);

--
-- Indexes for table `codename_status`
--
ALTER TABLE `codename_status`
  ADD PRIMARY KEY (`status_id`);

--
-- Indexes for table `export_excel`
--
ALTER TABLE `export_excel`
  ADD PRIMARY KEY (`export_excel_id`);

--
-- Indexes for table `export_metadata`
--
ALTER TABLE `export_metadata`
  ADD PRIMARY KEY (`export_metadata_id`);

--
-- Indexes for table `group_permission_detail`
--
ALTER TABLE `group_permission_detail`
  ADD PRIMARY KEY (`group_permission_detail_id`);

--
-- Indexes for table `group_user`
--
ALTER TABLE `group_user`
  ADD PRIMARY KEY (`group_id`);

--
-- Indexes for table `group_user_detail`
--
ALTER TABLE `group_user_detail`
  ADD PRIMARY KEY (`group_user_detail_id`);

--
-- Indexes for table `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`log_id`);

--
-- Indexes for table `metadata`
--
ALTER TABLE `metadata`
  ADD PRIMARY KEY (`metadata_id`);

--
-- Indexes for table `metadata_permission`
--
ALTER TABLE `metadata_permission`
  ADD PRIMARY KEY (`metadata_permission_id`);

--
-- Indexes for table `sub_category`
--
ALTER TABLE `sub_category`
  ADD PRIMARY KEY (`sub_category_id`);

--
-- Indexes for table `token_register`
--
ALTER TABLE `token_register`
  ADD PRIMARY KEY (`token_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `category`
--
ALTER TABLE `category`
  MODIFY `category_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `codename_download_type`
--
ALTER TABLE `codename_download_type`
  MODIFY `download_type_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `codename_group_permission`
--
ALTER TABLE `codename_group_permission`
  MODIFY `group_permission_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `codename_import_status`
--
ALTER TABLE `codename_import_status`
  MODIFY `import_status_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `codename_metadata_status`
--
ALTER TABLE `codename_metadata_status`
  MODIFY `metadata_status_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `codename_mode_viewer`
--
ALTER TABLE `codename_mode_viewer`
  MODIFY `mode_viewer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `codename_previlage`
--
ALTER TABLE `codename_previlage`
  MODIFY `previlage_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `codename_schedule_mode`
--
ALTER TABLE `codename_schedule_mode`
  MODIFY `schedule_mode_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `codename_status`
--
ALTER TABLE `codename_status`
  MODIFY `status_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `export_excel`
--
ALTER TABLE `export_excel`
  MODIFY `export_excel_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `export_metadata`
--
ALTER TABLE `export_metadata`
  MODIFY `export_metadata_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `group_permission_detail`
--
ALTER TABLE `group_permission_detail`
  MODIFY `group_permission_detail_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `group_user`
--
ALTER TABLE `group_user`
  MODIFY `group_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `group_user_detail`
--
ALTER TABLE `group_user_detail`
  MODIFY `group_user_detail_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `log`
--
ALTER TABLE `log`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `metadata`
--
ALTER TABLE `metadata`
  MODIFY `metadata_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `metadata_permission`
--
ALTER TABLE `metadata_permission`
  MODIFY `metadata_permission_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sub_category`
--
ALTER TABLE `sub_category`
  MODIFY `sub_category_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `token_register`
--
ALTER TABLE `token_register`
  MODIFY `token_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
