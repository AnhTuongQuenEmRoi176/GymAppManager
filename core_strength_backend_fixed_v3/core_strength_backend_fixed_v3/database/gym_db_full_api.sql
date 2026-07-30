-- ============================================================================
-- CORE STRENGTH / APEX GYM - DATABASE ĐẦY ĐỦ CHO WINDOWS APP + FLUTTER APP
-- MySQL / MariaDB (XAMPP) - UTF8MB4
--
-- CẢNH BÁO: File này XÓA TOÀN BỘ database `gym_db` cũ rồi tạo lại từ đầu.
-- Hãy sao lưu dữ liệu thật trước khi chạy.
--
-- Tài khoản mẫu:
--   Windows Admin : admin       / admin123
--   Lễ tân        : receptionist / 123456
--   Flutter PT    : trainer     / 123456
--   Flutter Member: member      / 123456
--   Các tài khoản mẫu khác cũng dùng mật khẩu: 123456
-- ============================================================================

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP DATABASE IF EXISTS `gym_db`;
CREATE DATABASE `gym_db`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE `gym_db`;

-- ============================================================================
-- 1. PHÂN QUYỀN VÀ TÀI KHOẢN
-- ============================================================================

CREATE TABLE `roles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `display_name` VARCHAR(100) NULL,
  `description` VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_roles_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(100) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(200) NULL,
  `phone` VARCHAR(20) NULL,
  `email` VARCHAR(150) NULL,
  `role_id` INT NULL,
  `avatar` VARCHAR(500) NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `must_change_password` TINYINT(1) NOT NULL DEFAULT 0,
  `last_login_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_users_username` (`username`),
  KEY `idx_users_phone` (`phone`),
  KEY `idx_users_email` (`email`),
  KEY `idx_users_role_active` (`role_id`, `is_active`),
  CONSTRAINT `fk_users_role`
    FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `receptionists` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NULL,
  `base_salary` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `note` VARCHAR(500) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_receptionists_user` (`user_id`),
  KEY `idx_receptionists_status` (`start_date`, `end_date`),
  CONSTRAINT `fk_receptionists_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `password_reset_otps` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `otp_hash` VARCHAR(255) NOT NULL,
  `expires_at` DATETIME NOT NULL,
  `used_at` DATETIME NULL,
  `attempt_count` INT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_password_reset_user` (`user_id`, `expires_at`, `used_at`),
  CONSTRAINT `fk_password_reset_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `refresh_tokens` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `token_hash` VARCHAR(255) NOT NULL,
  `expires_at` DATETIME NOT NULL,
  `revoked_at` DATETIME NULL,
  `device_name` VARCHAR(150) NULL,
  `ip_address` VARCHAR(45) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_refresh_token_hash` (`token_hash`),
  KEY `idx_refresh_user` (`user_id`, `revoked_at`, `expires_at`),
  CONSTRAINT `fk_refresh_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. HỒ SƠ PT VÀ HỘI VIÊN
-- ============================================================================

CREATE TABLE `trainers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `specialty` VARCHAR(200) NULL,
  `start_date` DATE NULL,
  `end_date` DATE NULL,
  `base_salary` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `session_commission_percent` DECIMAL(5,2) NOT NULL DEFAULT 0.50,
  `bio` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_trainers_user` (`user_id`),
  KEY `idx_trainers_dates` (`start_date`, `end_date`),
  CONSTRAINT `fk_trainers_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `members` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `dob` DATE NULL,
  `gender` ENUM('Nam','Nữ','Khác') NULL,
  `address` VARCHAR(255) NULL,
  `emergency_contact_name` VARCHAR(200) NULL,
  `emergency_contact_phone` VARCHAR(20) NULL,
  `joined_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` ENUM('active','inactive','suspended') NOT NULL DEFAULT 'active',
  `note` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_members_user` (`user_id`),
  KEY `idx_members_status` (`status`, `joined_at`),
  CONSTRAINT `fk_members_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. GÓI TẬP VÀ ĐĂNG KÝ GÓI
-- ============================================================================

CREATE TABLE `packages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(150) NOT NULL,
  `package_type` ENUM('GYM','PT','COMBO') NOT NULL DEFAULT 'GYM',
  `description` TEXT NULL,
  `price` DECIMAL(12,2) NOT NULL,
  `duration_days` INT NOT NULL,
  `sessions` INT NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `idx_packages_type_active_price` (`package_type`, `is_active`, `price`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `member_packages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `member_id` INT NOT NULL,
  `package_id` INT NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  `sessions_total` INT NULL,
  `sessions_remaining` INT NULL,
  `pt_id` INT NULL,
  `pt_session_unit_price` DECIMAL(12,2) NULL,
  `price_paid` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `status` ENUM('pending','active','expired','cancelled') NOT NULL DEFAULT 'active',
  `created_by` INT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `idx_member_packages_member_status` (`member_id`, `status`, `end_date`),
  KEY `idx_member_packages_pt_status` (`pt_id`, `status`, `end_date`),
  KEY `idx_member_packages_package` (`package_id`),
  CONSTRAINT `fk_member_packages_member`
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_member_packages_package`
    FOREIGN KEY (`package_id`) REFERENCES `packages` (`id`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_member_packages_pt`
    FOREIGN KEY (`pt_id`) REFERENCES `trainers` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_member_packages_creator`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `membership_requests` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `member_id` INT NOT NULL,
  `request_type` ENUM('new_package','renew','upgrade','cancel','change_trainer') NOT NULL,
  `requested_package_id` INT NULL,
  `requested_trainer_id` INT NULL,
  `note` TEXT NULL,
  `status` ENUM('pending','approved','rejected','cancelled') NOT NULL DEFAULT 'pending',
  `reviewed_by` INT NULL,
  `reviewed_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_membership_requests_member` (`member_id`, `status`, `created_at`),
  CONSTRAINT `fk_membership_requests_member`
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT `fk_membership_requests_package`
    FOREIGN KEY (`requested_package_id`) REFERENCES `packages` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_membership_requests_trainer`
    FOREIGN KEY (`requested_trainer_id`) REFERENCES `trainers` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_membership_requests_reviewer`
    FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. LỊCH TẬP, LỊCH DẠY VÀ KHUNG GIỜ RẢNH
-- ============================================================================

CREATE TABLE `training_schedules` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `trainer_id` INT NOT NULL,
  `member_id` INT NOT NULL,
  `member_package_id` INT NULL,
  `title` VARCHAR(200) NOT NULL,
  `start_at` DATETIME NOT NULL,
  `end_at` DATETIME NOT NULL,
  `location` VARCHAR(200) NULL,
  `note` TEXT NULL,
  `status` ENUM('pending','upcoming','completed','cancelled','no_show') NOT NULL DEFAULT 'upcoming',
  `created_by` INT NULL,
  `cancelled_by` INT NULL,
  `cancelled_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `idx_schedule_trainer_time` (`trainer_id`, `start_at`, `status`),
  KEY `idx_schedule_member_time` (`member_id`, `start_at`, `status`),
  CONSTRAINT `fk_schedule_trainer`
    FOREIGN KEY (`trainer_id`) REFERENCES `trainers` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT `fk_schedule_member`
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT `fk_schedule_member_package`
    FOREIGN KEY (`member_package_id`) REFERENCES `member_packages` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_schedule_creator`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_schedule_cancelled_by`
    FOREIGN KEY (`cancelled_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `trainer_availability` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `trainer_id` INT NOT NULL,
  `available_date` DATE NOT NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  `status` ENUM('available','busy','off') NOT NULL DEFAULT 'available',
  `note` VARCHAR(500) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_trainer_availability` (`trainer_id`, `available_date`, `start_time`, `end_time`),
  KEY `idx_trainer_availability_date` (`available_date`, `status`),
  CONSTRAINT `fk_trainer_availability_trainer`
    FOREIGN KEY (`trainer_id`) REFERENCES `trainers` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. QR, CHECK-IN VÀ BUỔI PT
-- ============================================================================

CREATE TABLE `qr_demo` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `code` VARCHAR(255) NOT NULL,
  `entity_type` ENUM('member','trainer') NOT NULL,
  `entity_id` INT NOT NULL,
  `generated_by` INT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_qr_demo_code` (`code`),
  KEY `idx_qr_demo_entity` (`entity_type`, `entity_id`),
  CONSTRAINT `fk_qr_demo_generated_by`
    FOREIGN KEY (`generated_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `qr_tokens` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `token_id` CHAR(36) NOT NULL,
  `user_id` INT NOT NULL,
  `entity_type` ENUM('member','trainer') NOT NULL,
  `entity_id` INT NOT NULL,
  `token_hash` VARCHAR(255) NOT NULL,
  `expires_at` DATETIME NOT NULL,
  `used_at` DATETIME NULL,
  `used_by` INT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_qr_token_id` (`token_id`),
  UNIQUE KEY `uq_qr_token_hash` (`token_hash`),
  KEY `idx_qr_lookup` (`user_id`, `expires_at`, `used_at`),
  CONSTRAINT `fk_qr_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT `fk_qr_used_by`
    FOREIGN KEY (`used_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `checkins` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `member_id` INT NULL,
  `trainer_id` INT NULL,
  `scanned_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `scanner_user_id` INT NULL,
  `source` VARCHAR(50) NULL,
  `qr_payload` VARCHAR(500) NULL,
  `photo` VARCHAR(500) NULL,
  `status` ENUM('pending','confirmed','rejected') NOT NULL DEFAULT 'confirmed',
  `confirmed_at` DATETIME NULL,
  `pair_group_id` CHAR(36) NULL,
  `idempotency_key` VARCHAR(100) NULL,
  `device_id` VARCHAR(150) NULL,
  `location` VARCHAR(200) NULL,
  `note` VARCHAR(500) NULL,
  KEY `idx_checkins_member_time` (`member_id`, `scanned_at`),
  KEY `idx_checkins_trainer_time` (`trainer_id`, `scanned_at`),
  KEY `idx_checkins_scanner_time` (`scanner_user_id`, `scanned_at`),
  KEY `idx_checkin_pair` (`pair_group_id`),
  UNIQUE KEY `uq_checkin_idempotency` (`idempotency_key`),
  CONSTRAINT `fk_checkins_member`
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_checkins_trainer`
    FOREIGN KEY (`trainer_id`) REFERENCES `trainers` (`id`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_checkins_scanner`
    FOREIGN KEY (`scanner_user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `pt_sessions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `trainer_id` INT NOT NULL,
  `member_id` INT NOT NULL,
  `member_package_id` INT NULL,
  `schedule_id` BIGINT NULL,
  `session_date` DATETIME NOT NULL,
  `confirmed_by` INT NULL,
  `status` ENUM('pending','confirmed','cancelled','no_show') NOT NULL DEFAULT 'confirmed',
  `commission_rate` DECIMAL(5,2) NOT NULL DEFAULT 0.50,
  `commission_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `note` VARCHAR(500) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_pt_sessions_trainer_date` (`trainer_id`, `session_date`, `status`),
  KEY `idx_pt_sessions_member_date` (`member_id`, `session_date`, `status`),
  CONSTRAINT `fk_pt_sessions_trainer`
    FOREIGN KEY (`trainer_id`) REFERENCES `trainers` (`id`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_pt_sessions_member`
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT `fk_pt_sessions_member_package`
    FOREIGN KEY (`member_package_id`) REFERENCES `member_packages` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_pt_sessions_schedule`
    FOREIGN KEY (`schedule_id`) REFERENCES `training_schedules` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_pt_sessions_confirmed_by`
    FOREIGN KEY (`confirmed_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 6. THANH TOÁN, GIAO DỊCH, CHI PHÍ VÀ LƯƠNG
-- ============================================================================

CREATE TABLE `transactions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `type` ENUM('payment','salary','refund','other') NOT NULL,
  `amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `description` TEXT NULL,
  `created_by` INT NULL,
  `reference_type` VARCHAR(50) NULL,
  `reference_id` BIGINT NULL,
  KEY `idx_transactions_type_date` (`type`, `date`),
  KEY `idx_transactions_creator` (`created_by`, `date`),
  CONSTRAINT `fk_transactions_created_by`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `payments` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `payment_code` VARCHAR(50) NOT NULL,
  `member_id` INT NULL,
  `member_package_id` INT NULL,
  `amount` DECIMAL(12,2) NOT NULL,
  `method` ENUM('cash','bank_transfer','card','e_wallet','other') NOT NULL DEFAULT 'cash',
  `status` ENUM('pending','paid','failed','refunded','cancelled') NOT NULL DEFAULT 'paid',
  `paid_at` DATETIME NULL,
  `confirmed_by` INT NULL,
  `note` VARCHAR(500) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_payments_code` (`payment_code`),
  KEY `idx_payments_member_time` (`member_id`, `created_at`),
  KEY `idx_payments_status_time` (`status`, `created_at`),
  CONSTRAINT `fk_payments_member`
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_payments_member_package`
    FOREIGN KEY (`member_package_id`) REFERENCES `member_packages` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_payments_confirmed_by`
    FOREIGN KEY (`confirmed_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `expenses` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `category` VARCHAR(100) NOT NULL,
  `amount` DECIMAL(12,2) NOT NULL,
  `expense_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `description` TEXT NULL,
  `created_by` INT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_expenses_date_category` (`expense_date`, `category`),
  CONSTRAINT `fk_expenses_created_by`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `payroll_periods` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `period_month` TINYINT NOT NULL,
  `period_year` SMALLINT NOT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  `status` ENUM('draft','calculated','paid','cancelled') NOT NULL DEFAULT 'draft',
  `total_amount` DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  `calculated_by` INT NULL,
  `calculated_at` DATETIME NULL,
  `paid_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_payroll_period` (`period_month`, `period_year`),
  CONSTRAINT `fk_payroll_period_calculated_by`
    FOREIGN KEY (`calculated_by`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `payroll_items` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `payroll_period_id` BIGINT NOT NULL,
  `employee_user_id` INT NULL,
  `employee_type` ENUM('trainer','receptionist') NOT NULL,
  `trainer_id` INT NULL,
  `receptionist_id` INT NULL,
  `base_salary` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `session_count` INT NOT NULL DEFAULT 0,
  `session_income` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `bonus` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `deduction` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `note` VARCHAR(500) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_payroll_employee_period` (`payroll_period_id`, `employee_user_id`),
  CONSTRAINT `fk_payroll_items_period`
    FOREIGN KEY (`payroll_period_id`) REFERENCES `payroll_periods` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT `fk_payroll_items_user`
    FOREIGN KEY (`employee_user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_payroll_items_trainer`
    FOREIGN KEY (`trainer_id`) REFERENCES `trainers` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT `fk_payroll_items_receptionist`
    FOREIGN KEY (`receptionist_id`) REFERENCES `receptionists` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 7. THÔNG BÁO, THIẾT BỊ VÀ REALTIME
-- ============================================================================

CREATE TABLE `notifications` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `type` VARCHAR(50) NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `body` TEXT NOT NULL,
  `data_json` JSON NULL,
  `is_read` TINYINT(1) NOT NULL DEFAULT 0,
  `read_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_notification_user` (`user_id`, `is_read`, `created_at`),
  CONSTRAINT `fk_notification_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `device_tokens` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `token` VARCHAR(500) NOT NULL,
  `platform` ENUM('android','ios','web') NOT NULL,
  `device_name` VARCHAR(150) NULL,
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `last_seen_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_device_token` (`token`),
  KEY `idx_device_user_active` (`user_id`, `is_active`),
  CONSTRAINT `fk_device_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Transactional Outbox: backend/WebSocket đọc các sự kiện chưa gửi.
CREATE TABLE `outbox_events` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `event_type` VARCHAR(100) NOT NULL,
  `aggregate_type` VARCHAR(100) NULL,
  `aggregate_id` VARCHAR(100) NULL,
  `target_user_id` INT NULL,
  `payload_json` JSON NOT NULL,
  `status` ENUM('pending','processing','published','failed') NOT NULL DEFAULT 'pending',
  `retry_count` INT NOT NULL DEFAULT 0,
  `available_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `published_at` DATETIME NULL,
  `last_error` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `idx_outbox_dispatch` (`status`, `available_at`, `id`),
  KEY `idx_outbox_target` (`target_user_id`, `created_at`),
  CONSTRAINT `fk_outbox_target_user`
    FOREIGN KEY (`target_user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 8. DỮ LIỆU MẪU
-- ============================================================================

SET @NOW_VALUE = NOW();
SET @TODAY_VALUE = CURDATE();
SET @MONTH_START = DATE_FORMAT(CURDATE(), '%Y-%m-01');
SET @MONTH_END = LAST_DAY(CURDATE());

-- 8.1 Roles
INSERT INTO `roles` (`id`, `name`, `display_name`, `description`) VALUES
  (1, 'admin',        'Quản trị viên',  'Toàn quyền trên Windows App'),
  (2, 'receptionist', 'Lễ tân',         'Vận hành quầy, check-in và quản lý nghiệp vụ cơ bản'),
  (3, 'MEMBER',       'Hội viên',       'Sử dụng Flutter Mobile dành cho hội viên'),
  (4, 'TRAINER',      'Huấn luyện viên','Sử dụng Flutter Mobile dành cho PT');

-- Mật khẩu đã mã hóa bcrypt:
-- admin123 => $2b$12$Px5N6KGLv7MPTcxwjC3LKu0GauiYqDtAiq.CJgIQDerm4pG8iQYWe
-- 123456   => $2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy

-- 8.2 Users
INSERT INTO `users`
(`id`, `username`, `password_hash`, `full_name`, `phone`, `email`, `role_id`, `avatar`, `is_active`, `must_change_password`, `created_at`)
VALUES
  (1, 'admin',        '$2b$12$Px5N6KGLv7MPTcxwjC3LKu0GauiYqDtAiq.CJgIQDerm4pG8iQYWe', 'Quản trị viên',     '0900000001', 'admin@corestrength.vn',       1, NULL,           1, 0, DATE_SUB(@NOW_VALUE, INTERVAL 400 DAY)),
  (2, 'receptionist', '$2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy', 'Lễ tân Thu Hà',     '0900000002', 'le.tan@corestrength.vn',      2, NULL,           1, 0, DATE_SUB(@NOW_VALUE, INTERVAL 300 DAY)),
  (3, 'trainer',      '$2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy', 'PT Minh Quân',      '0901234567', 'minhquan@corestrength.vn',     4, 'trainer1.png', 1, 0, DATE_SUB(@NOW_VALUE, INTERVAL 280 DAY)),
  (4, 'trainer02',    '$2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy', 'PT Ngọc Anh',       '0902345678', 'ngocanh@corestrength.vn',      4, NULL,           1, 0, DATE_SUB(@NOW_VALUE, INTERVAL 220 DAY)),
  (5, 'member',       '$2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy', 'Nguyễn Minh Tuấn',  '0987654321', 'member@corestrength.vn',       3, 'member1.png',  1, 0, DATE_SUB(@NOW_VALUE, INTERVAL 150 DAY)),
  (6, 'member02',     '$2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy', 'Nguyễn Văn A',      '0904567890', 'member02@corestrength.vn',     3, 'member2.png',  1, 0, DATE_SUB(@NOW_VALUE, INTERVAL 120 DAY)),
  (7, 'member03',     '$2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy', 'Lê Hoàng Nam',      '0905678901', 'member03@corestrength.vn',     3, 'member3.png',  1, 0, DATE_SUB(@NOW_VALUE, INTERVAL 100 DAY)),
  (8, 'member04',     '$2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy', 'Trần Thị Mai',      '0906789012', 'member04@corestrength.vn',     3, 'member5.png',  1, 0, DATE_SUB(@NOW_VALUE, INTERVAL 80 DAY)),
  (9, 'member05',     '$2b$12$3Uzqxyn/fWnKUmo1RzR.meToBLRCLxZErBZRvSNA3VDyut5jNZzRy', 'Bùi Quốc Huy',      '0907890123', 'member05@corestrength.vn',     3, NULL,           0, 0, DATE_SUB(@NOW_VALUE, INTERVAL 200 DAY));

-- 8.3 Receptionist profile
INSERT INTO `receptionists`
(`id`, `user_id`, `start_date`, `end_date`, `base_salary`, `note`)
VALUES
  (1, 2, DATE_SUB(@TODAY_VALUE, INTERVAL 300 DAY), NULL, 7500000, 'Ca hành chính và ca tối luân phiên');

-- 8.4 Trainers
INSERT INTO `trainers`
(`id`, `user_id`, `specialty`, `start_date`, `end_date`, `base_salary`, `session_commission_percent`, `bio`)
VALUES
  (1, 3, 'Strength, Thể hình, Tăng cơ', DATE_SUB(@TODAY_VALUE, INTERVAL 280 DAY), NULL, 9000000, 0.50, 'Chuyên huấn luyện sức mạnh và tăng cơ.'),
  (2, 4, 'Yoga, Cardio, Giảm mỡ',       DATE_SUB(@TODAY_VALUE, INTERVAL 220 DAY), NULL, 8500000, 0.50, 'Chuyên yoga, cardio và cải thiện thể lực.');

-- 8.5 Members
INSERT INTO `members`
(`id`, `user_id`, `dob`, `gender`, `address`, `emergency_contact_name`, `emergency_contact_phone`, `joined_at`, `status`, `note`)
VALUES
  (1, 5, '1998-12-15', 'Nam', 'Cầu Giấy, Hà Nội',    'Nguyễn Văn Bình', '0911000001', DATE_SUB(@NOW_VALUE, INTERVAL 150 DAY), 'active',   'Mục tiêu tăng cơ và cải thiện sức mạnh.'),
  (2, 6, '1996-04-20', 'Nam', 'Nam Từ Liêm, Hà Nội', 'Trần Thị Lan',    '0911000002', DATE_SUB(@NOW_VALUE, INTERVAL 120 DAY), 'active',   'Tập duy trì sức khỏe.'),
  (3, 7, '2000-09-10', 'Nam', 'Thanh Xuân, Hà Nội',  'Lê Văn Sơn',      '0911000003', DATE_SUB(@NOW_VALUE, INTERVAL 100 DAY), 'active',   'Cần theo dõi số buổi PT còn lại.'),
  (4, 8, '1999-02-28', 'Nữ',  'Đống Đa, Hà Nội',     'Trần Văn Nam',    '0911000004', DATE_SUB(@NOW_VALUE, INTERVAL 80 DAY),  'active',   NULL),
  (5, 9, '1995-07-12', 'Nam', 'Hà Đông, Hà Nội',      'Bùi Thị Hoa',     '0911000005', DATE_SUB(@NOW_VALUE, INTERVAL 200 DAY), 'inactive', 'Đã hết hạn gói và tạm ngưng tài khoản.');

-- 8.6 Packages
INSERT INTO `packages`
(`id`, `name`, `package_type`, `description`, `price`, `duration_days`, `sessions`, `is_active`)
VALUES
  (1, 'Gói GYM 1 Tháng',       'GYM',   'Tập tự do trong 30 ngày.',                         500000,   30, NULL, 1),
  (2, 'Gói GYM Gold 3 Tháng',  'GYM',   'Tập tự do 90 ngày, ưu tiên khu vực Gold.',        1300000,  90, NULL, 1),
  (3, 'Gói GYM 6 Tháng',       'GYM',   'Tập tự do trong 180 ngày.',                       2400000, 180, NULL, 1),
  (4, 'Gói PT 10 Buổi',        'PT',    '10 buổi PT, đơn giá 700.000 đồng/buổi.',          7000000,  60, 10,   1),
  (5, 'Gói PT 30 Buổi',        'PT',    '30 buổi PT, đơn giá 600.000 đồng/buổi.',         18000000, 180, 30,  1),
  (6, 'Gói PT 50 Buổi',        'PT',    '50 buổi PT, đơn giá 500.000 đồng/buổi.',         25000000, 300, 50,  1),
  (7, 'Gói PT 72 Buổi',        'PT',    '72 buổi PT, đơn giá 400.000 đồng/buổi.',         28800000, 365, 72,  1),
  (8, 'Gold + PT 30 Buổi',     'COMBO', 'Gói Gold 3 tháng kết hợp 30 buổi PT.',           19300000,  90, 30,  1),
  (9, 'Gói GYM Vĩnh Viễn',     'GYM',   'Gói tập dài hạn dùng cho dữ liệu demo.',          5000000,36500,NULL, 1);

-- 8.7 Member packages, gồm cả gói hiện tại và lịch sử đã hết hạn
INSERT INTO `member_packages`
(`id`, `member_id`, `package_id`, `start_date`, `end_date`, `sessions_total`, `sessions_remaining`, `pt_id`, `pt_session_unit_price`, `price_paid`, `status`, `created_by`, `created_at`)
VALUES
  (1, 1, 8, DATE_SUB(@TODAY_VALUE, INTERVAL 45 DAY), DATE_ADD(@TODAY_VALUE, INTERVAL 45 DAY), 30, 12, 1, 600000, 19300000, 'active',  2, DATE_SUB(@NOW_VALUE, INTERVAL 45 DAY)),
  (2, 2, 2, DATE_SUB(@TODAY_VALUE, INTERVAL 20 DAY), DATE_ADD(@TODAY_VALUE, INTERVAL 70 DAY), NULL, NULL, NULL, NULL, 1300000, 'active', 2, DATE_SUB(@NOW_VALUE, INTERVAL 20 DAY)),
  (3, 3, 4, DATE_SUB(@TODAY_VALUE, INTERVAL 10 DAY), DATE_ADD(@TODAY_VALUE, INTERVAL 50 DAY), 10, 2, 1, 700000, 7000000,  'active', 2, DATE_SUB(@NOW_VALUE, INTERVAL 10 DAY)),
  (4, 4, 5, DATE_SUB(@TODAY_VALUE, INTERVAL 30 DAY), DATE_ADD(@TODAY_VALUE, INTERVAL 150 DAY),30, 24, 2, 600000, 18000000, 'active', 2, DATE_SUB(@NOW_VALUE, INTERVAL 30 DAY)),
  (5, 1, 1, DATE_SUB(@TODAY_VALUE, INTERVAL 150 DAY),DATE_SUB(@TODAY_VALUE, INTERVAL 120 DAY),NULL,NULL,NULL,NULL,500000, 'expired',2,DATE_SUB(@NOW_VALUE, INTERVAL 150 DAY)),
  (6, 5, 1, DATE_SUB(@TODAY_VALUE, INTERVAL 90 DAY), DATE_SUB(@TODAY_VALUE, INTERVAL 60 DAY), NULL,NULL,NULL,NULL,500000, 'expired',2,DATE_SUB(@NOW_VALUE, INTERVAL 90 DAY));

-- 8.8 Schedules
INSERT INTO `training_schedules`
(`id`, `trainer_id`, `member_id`, `member_package_id`, `title`, `start_at`, `end_at`, `location`, `note`, `status`, `created_by`)
VALUES
  (1, 1, 1, 1, 'Tập Ngực - Vai', DATE_ADD(@NOW_VALUE, INTERVAL 2 HOUR),  DATE_ADD(@NOW_VALUE, INTERVAL 3 HOUR),  'Khu PT tầng 2', 'Ưu tiên bài đẩy ngực.', 'upcoming', 2),
  (2, 1, 1, 1, 'Tập Chân',       DATE_ADD(@NOW_VALUE, INTERVAL 1 DAY),   DATE_ADD(DATE_ADD(@NOW_VALUE, INTERVAL 1 DAY), INTERVAL 90 MINUTE), 'Khu tập chính', NULL, 'upcoming', 2),
  (3, 1, 2, NULL, 'Đánh giá thể lực', DATE_ADD(@NOW_VALUE, INTERVAL 5 HOUR), DATE_ADD(@NOW_VALUE, INTERVAL 6 HOUR), 'Phòng đánh giá', 'Buổi đánh giá ban đầu.', 'upcoming', 2),
  (4, 1, 3, 3, 'Cardio & Core',   DATE_ADD(@NOW_VALUE, INTERVAL 2 DAY),   DATE_ADD(DATE_ADD(@NOW_VALUE, INTERVAL 2 DAY), INTERVAL 60 MINUTE), 'Khu Cardio', NULL, 'upcoming', 2),
  (5, 2, 4, 4, 'Yoga & Mobility', DATE_ADD(@NOW_VALUE, INTERVAL 1 DAY),   DATE_ADD(DATE_ADD(@NOW_VALUE, INTERVAL 1 DAY), INTERVAL 60 MINUTE), 'Phòng Yoga', NULL, 'upcoming', 2),
  (6, 1, 1, 1, 'Tập Lưng - Tay',  DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY),   DATE_ADD(DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), INTERVAL 60 MINUTE), 'Khu PT tầng 2', NULL, 'completed', 2),
  (7, 2, 4, 4, 'Cardio nhẹ',      DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY),   DATE_ADD(DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY), INTERVAL 60 MINUTE), 'Khu Cardio', NULL, 'completed', 2);

-- 8.9 Trainer availability
INSERT INTO `trainer_availability`
(`trainer_id`, `available_date`, `start_time`, `end_time`, `status`, `note`)
VALUES
  (1, @TODAY_VALUE,                         '08:00:00', '12:00:00', 'available', NULL),
  (1, @TODAY_VALUE,                         '14:00:00', '21:00:00', 'available', 'Có lịch xen kẽ, kiểm tra training_schedules.'),
  (1, DATE_ADD(@TODAY_VALUE, INTERVAL 1 DAY),'08:00:00', '20:00:00', 'available', NULL),
  (2, @TODAY_VALUE,                         '09:00:00', '17:00:00', 'available', NULL),
  (2, DATE_ADD(@TODAY_VALUE, INTERVAL 1 DAY),'09:00:00', '18:00:00', 'available', NULL);

-- 8.10 QR demo
INSERT INTO `qr_demo`
(`id`, `code`, `entity_type`, `entity_id`, `generated_by`)
VALUES
  (1, 'GYM:MEMBER:1:DEMO',  'member',  1, 2),
  (2, 'GYM:TRAINER:1:DEMO', 'trainer', 1, 2),
  (3, 'GYM:MEMBER:2:DEMO',  'member',  2, 2);

-- 8.11 QR token mẫu đã sử dụng (không dùng để đăng nhập/check-in thật)
INSERT INTO `qr_tokens`
(`id`, `token_id`, `user_id`, `entity_type`, `entity_id`, `token_hash`, `expires_at`, `used_at`, `used_by`, `created_at`)
VALUES
  (1, '11111111-1111-4111-8111-111111111111', 5, 'member', 1, 'demo-member-token-hash-used', DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), 2, DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY)),
  (2, '22222222-2222-4222-8222-222222222222', 3, 'trainer',1, 'demo-trainer-token-hash-used',DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), 2, DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY));

-- 8.12 Check-ins
INSERT INTO `checkins`
(`id`, `member_id`, `trainer_id`, `scanned_at`, `scanner_user_id`, `source`, `qr_payload`, `status`, `confirmed_at`, `pair_group_id`, `idempotency_key`, `device_id`, `location`, `note`)
VALUES
  (1, 1, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), 2, 'QR Mobile', 'signed-member-token-001', 'confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'checkin-demo-001', 'WINDOWS-CAM-01', 'Quầy check-in chính', 'Check-in cặp với PT Minh Quân'),
  (2, NULL, 1, DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), 2, 'QR Mobile', 'signed-trainer-token-001','confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', 'checkin-demo-002', 'WINDOWS-CAM-01', 'Quầy check-in chính', 'Check-in cặp với Nguyễn Minh Tuấn'),
  (3, 1, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY), 2, 'QR Mobile', 'signed-member-token-003', 'confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY), NULL, 'checkin-demo-003', 'WINDOWS-CAM-01', 'Quầy check-in chính', NULL),
  (4, 1, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 6 DAY), 2, 'QR Demo',   'GYM:MEMBER:1:DEMO',       'confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 6 DAY), NULL, 'checkin-demo-004', 'WINDOWS-CAM-01', 'Quầy check-in chính', NULL),
  (5, 2, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), 2, 'QR Mobile', 'signed-member-token-005', 'confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), NULL, 'checkin-demo-005', 'WINDOWS-CAM-01', 'Quầy check-in chính', NULL),
  (6, 3, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), 2, 'QR Mobile', 'signed-member-token-006', 'confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb', 'checkin-demo-006', 'WINDOWS-CAM-01', 'Quầy check-in chính', NULL),
  (7, NULL, 1, DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), 2, 'QR Mobile', 'signed-trainer-token-007','confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb', 'checkin-demo-007', 'WINDOWS-CAM-01', 'Quầy check-in chính', NULL),
  (8, 4, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY), 2, 'QR Mobile', 'signed-member-token-008', 'confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY), 'cccccccc-cccc-4ccc-8ccc-cccccccccccc', 'checkin-demo-008', 'WINDOWS-CAM-01', 'Quầy check-in chính', NULL),
  (9, NULL, 2, DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY), 2, 'QR Mobile', 'signed-trainer-token-009','confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY), 'cccccccc-cccc-4ccc-8ccc-cccccccccccc', 'checkin-demo-009', 'WINDOWS-CAM-01', 'Quầy check-in chính', NULL),
  (10,2, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 8 DAY), 2, 'Manual',    NULL,                       'confirmed', DATE_SUB(@NOW_VALUE, INTERVAL 8 DAY), NULL, 'checkin-demo-010', 'RECEPTION-01', 'Quầy check-in chính', 'Lễ tân nhập thủ công');

-- 8.13 PT sessions đã xác nhận
INSERT INTO `pt_sessions`
(`id`, `trainer_id`, `member_id`, `member_package_id`, `schedule_id`, `session_date`, `confirmed_by`, `status`, `commission_rate`, `commission_amount`, `note`)
VALUES
  (1, 1, 1, 1, 6, DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), 2, 'confirmed', 0.50, 96500, 'Buổi tập hoàn thành tốt.'),
  (2, 1, 1, 1, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 5 DAY), 2, 'confirmed', 0.50, 96500, NULL),
  (3, 1, 3, 3, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 2 DAY), 2, 'confirmed', 0.50, 35000, 'Hội viên còn ít buổi PT.'),
  (4, 2, 4, 4, 7, DATE_SUB(@NOW_VALUE, INTERVAL 3 DAY), 2, 'confirmed', 0.50, 90000, NULL),
  (5, 2, 4, 4, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 7 DAY), 2, 'confirmed', 0.50, 90000, NULL),
  (6, 1, 1, 1, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 10 DAY),2, 'confirmed', 0.50, 96500, NULL),
  (7, 1, 1, 1, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 14 DAY),2, 'confirmed', 0.50, 96500, NULL),
  (8, 2, 4, 4, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 12 DAY),2, 'confirmed', 0.50, 90000, NULL);

-- 8.14 Payments
INSERT INTO `payments`
(`id`, `payment_code`, `member_id`, `member_package_id`, `amount`, `method`, `status`, `paid_at`, `confirmed_by`, `note`, `created_at`)
VALUES
  (1, 'PAY-DEMO-0001', 1, 1, 19300000, 'bank_transfer', 'paid', DATE_SUB(@NOW_VALUE, INTERVAL 45 DAY), 2, 'Thanh toán gói Gold + PT 30 buổi', DATE_SUB(@NOW_VALUE, INTERVAL 45 DAY)),
  (2, 'PAY-DEMO-0002', 2, 2, 1300000,  'cash',          'paid', DATE_SUB(@NOW_VALUE, INTERVAL 20 DAY), 2, 'Thanh toán gói GYM Gold', DATE_SUB(@NOW_VALUE, INTERVAL 20 DAY)),
  (3, 'PAY-DEMO-0003', 3, 3, 7000000,  'card',          'paid', DATE_SUB(@NOW_VALUE, INTERVAL 10 DAY), 2, 'Thanh toán gói PT 10 buổi', DATE_SUB(@NOW_VALUE, INTERVAL 10 DAY)),
  (4, 'PAY-DEMO-0004', 4, 4, 18000000, 'bank_transfer', 'paid', DATE_SUB(@NOW_VALUE, INTERVAL 30 DAY), 2, 'Thanh toán gói PT 30 buổi', DATE_SUB(@NOW_VALUE, INTERVAL 30 DAY));

-- 8.15 Transactions tương ứng với thanh toán
INSERT INTO `transactions`
(`id`, `type`, `amount`, `date`, `description`, `created_by`, `reference_type`, `reference_id`)
VALUES
  (1, 'payment', 19300000, DATE_SUB(@NOW_VALUE, INTERVAL 45 DAY), 'Thu tiền Gold + PT 30 buổi - Nguyễn Minh Tuấn', 2, 'payment', 1),
  (2, 'payment', 1300000,  DATE_SUB(@NOW_VALUE, INTERVAL 20 DAY), 'Thu tiền GYM Gold - Nguyễn Văn A',               2, 'payment', 2),
  (3, 'payment', 7000000,  DATE_SUB(@NOW_VALUE, INTERVAL 10 DAY), 'Thu tiền PT 10 buổi - Lê Hoàng Nam',            2, 'payment', 3),
  (4, 'payment', 18000000, DATE_SUB(@NOW_VALUE, INTERVAL 30 DAY), 'Thu tiền PT 30 buổi - Trần Thị Mai',            2, 'payment', 4),
  (5, 'refund',  200000,   DATE_SUB(@NOW_VALUE, INTERVAL 5 DAY),  'Hoàn tiền điều chỉnh dịch vụ',                  1, 'manual', NULL);

-- 8.16 Expenses
INSERT INTO `expenses`
(`id`, `category`, `amount`, `expense_date`, `description`, `created_by`)
VALUES
  (1, 'Điện nước',       6500000, DATE_SUB(@NOW_VALUE, INTERVAL 8 DAY),  'Chi phí điện nước tháng hiện tại', 1),
  (2, 'Bảo trì thiết bị',3200000, DATE_SUB(@NOW_VALUE, INTERVAL 12 DAY), 'Bảo trì máy chạy bộ và giàn tạ',   1),
  (3, 'Marketing',       2500000, DATE_SUB(@NOW_VALUE, INTERVAL 15 DAY), 'Chiến dịch quảng cáo mạng xã hội', 1);

-- 8.17 Payroll current month
INSERT INTO `payroll_periods`
(`id`, `period_month`, `period_year`, `start_date`, `end_date`, `status`, `total_amount`, `calculated_by`, `calculated_at`)
VALUES
  (1, MONTH(@TODAY_VALUE), YEAR(@TODAY_VALUE), @MONTH_START, @MONTH_END, 'calculated', 25695000, 1, @NOW_VALUE);

INSERT INTO `payroll_items`
(`id`, `payroll_period_id`, `employee_user_id`, `employee_type`, `trainer_id`, `receptionist_id`, `base_salary`, `session_count`, `session_income`, `bonus`, `deduction`, `total_amount`, `note`)
VALUES
  (1, 1, 3, 'trainer',      1, NULL, 9000000, 5, 482500, 500000, 0, 9982500, 'Thu nhập PT Minh Quân theo dữ liệu demo'),
  (2, 1, 4, 'trainer',      2, NULL, 8500000, 3, 270000, 250000, 0, 9020000, 'Thu nhập PT Ngọc Anh theo dữ liệu demo'),
  (3, 1, 2, 'receptionist', NULL, 1, 7500000, 0, 0,      0,      0, 7500000, 'Lương lễ tân tháng hiện tại');

-- 8.18 Membership requests
INSERT INTO `membership_requests`
(`id`, `member_id`, `request_type`, `requested_package_id`, `requested_trainer_id`, `note`, `status`, `created_at`)
VALUES
  (1, 2, 'upgrade',        8, 1, 'Muốn nâng cấp sang gói có PT vào tháng tới.', 'pending', DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY)),
  (2, 3, 'renew',          4, 1, 'Gia hạn thêm 10 buổi với PT Minh Quân.',       'pending', @NOW_VALUE),
  (3, 1, 'change_trainer', NULL, 2, 'Yêu cầu đổi PT cho khung giờ cuối tuần.',   'rejected', DATE_SUB(@NOW_VALUE, INTERVAL 20 DAY));

-- 8.19 Notifications
INSERT INTO `notifications`
(`id`, `user_id`, `type`, `title`, `body`, `data_json`, `is_read`, `read_at`, `created_at`)
VALUES
  (1, 5, 'checkin', 'Check-in thành công', 'Buổi check-in của bạn đã được lễ tân xác nhận.', JSON_OBJECT('checkin_id', 1), 0, NULL, DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY)),
  (2, 5, 'schedule','Lịch tập sắp tới',     'Bạn có lịch Tập Ngực - Vai với PT Minh Quân.', JSON_OBJECT('schedule_id', 1), 0, NULL, @NOW_VALUE),
  (3, 3, 'kpi',     'KPI buổi PT cập nhật', 'Một buổi PT với Nguyễn Minh Tuấn đã được xác nhận.', JSON_OBJECT('pt_session_id', 1), 1, DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY)),
  (4, 7, 'package', 'Gói PT sắp hết buổi', 'Gói PT của bạn chỉ còn 2 buổi.', JSON_OBJECT('member_package_id', 3, 'sessions_remaining', 2), 0, NULL, @NOW_VALUE),
  (5, 8, 'schedule','Lịch Yoga ngày mai',   'Bạn có lịch Yoga & Mobility với PT Ngọc Anh.', JSON_OBJECT('schedule_id', 5), 0, NULL, @NOW_VALUE);

-- 8.20 Device tokens demo - token giả, thay bằng FCM token thật khi đăng nhập mobile
INSERT INTO `device_tokens`
(`id`, `user_id`, `token`, `platform`, `device_name`, `is_active`, `last_seen_at`)
VALUES
  (1, 5, 'demo-fcm-token-member-001',  'android', 'Android Emulator - Member', 1, @NOW_VALUE),
  (2, 3, 'demo-fcm-token-trainer-001', 'android', 'Android Emulator - Trainer',1, @NOW_VALUE);

-- 8.21 Refresh token mẫu đã thu hồi
INSERT INTO `refresh_tokens`
(`id`, `user_id`, `token_hash`, `expires_at`, `revoked_at`, `device_name`, `ip_address`, `created_at`)
VALUES
  (1, 5, 'demo-revoked-refresh-token-hash', DATE_ADD(@NOW_VALUE, INTERVAL 30 DAY), @NOW_VALUE, 'Android Emulator', '127.0.0.1', DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY));

-- 8.22 Outbox events mẫu đã publish
INSERT INTO `outbox_events`
(`id`, `event_type`, `aggregate_type`, `aggregate_id`, `target_user_id`, `payload_json`, `status`, `retry_count`, `available_at`, `published_at`, `created_at`)
VALUES
  (1, 'checkin.confirmed', 'checkin', '1', 5, JSON_OBJECT('checkin_id',1,'member_id',1,'status','confirmed'), 'published', 0, DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY)),
  (2, 'trainer.kpi_changed','trainer','1', 3, JSON_OBJECT('trainer_id',1,'pt_session_id',1), 'published', 0, DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY), DATE_SUB(@NOW_VALUE, INTERVAL 1 DAY));

-- ============================================================================
-- 9. VIEW HỖ TRỢ API / DASHBOARD
-- ============================================================================

CREATE OR REPLACE VIEW `v_active_member_packages` AS
SELECT
  mp.id AS member_package_id,
  mp.member_id,
  m.user_id AS member_user_id,
  u.full_name AS member_name,
  u.phone AS member_phone,
  mp.package_id,
  p.name AS package_name,
  p.package_type,
  mp.start_date,
  mp.end_date,
  mp.sessions_total,
  mp.sessions_remaining,
  mp.pt_id,
  tu.full_name AS trainer_name,
  mp.price_paid,
  mp.status
FROM member_packages mp
JOIN members m ON m.id = mp.member_id
JOIN users u ON u.id = m.user_id
JOIN packages p ON p.id = mp.package_id
LEFT JOIN trainers t ON t.id = mp.pt_id
LEFT JOIN users tu ON tu.id = t.user_id
WHERE mp.status = 'active'
  AND mp.start_date <= CURDATE()
  AND mp.end_date >= CURDATE();

CREATE OR REPLACE VIEW `v_trainer_monthly_income` AS
SELECT
  t.id AS trainer_id,
  t.user_id,
  u.full_name AS trainer_name,
  t.base_salary,
  COUNT(ps.id) AS confirmed_session_count,
  COALESCE(SUM(ps.commission_amount), 0) AS session_income,
  t.base_salary + COALESCE(SUM(ps.commission_amount), 0) AS estimated_total_income
FROM trainers t
JOIN users u ON u.id = t.user_id
LEFT JOIN pt_sessions ps
  ON ps.trainer_id = t.id
 AND ps.status = 'confirmed'
 AND YEAR(ps.session_date) = YEAR(CURDATE())
 AND MONTH(ps.session_date) = MONTH(CURDATE())
GROUP BY t.id, t.user_id, u.full_name, t.base_salary;

CREATE OR REPLACE VIEW `v_daily_revenue` AS
SELECT
  DATE(paid_at) AS revenue_date,
  COUNT(*) AS payment_count,
  SUM(amount) AS total_revenue
FROM payments
WHERE status = 'paid'
GROUP BY DATE(paid_at);

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- 10. KIỂM TRA NHANH SAU KHI IMPORT
-- ============================================================================
-- SELECT * FROM roles;
-- SELECT id, username, full_name, role_id, is_active FROM users;
-- SELECT * FROM v_active_member_packages;
-- SELECT * FROM v_trainer_monthly_income;
-- SELECT * FROM training_schedules ORDER BY start_at;
-- SELECT * FROM notifications ORDER BY created_at DESC;
-- ============================================================================
-- ============================================================================
-- REALTIME TRIGGERS CHO WINDOWS APP GHI TRỰC TIẾP MYSQL
-- Chạy file này sau gym_db_full.sql nếu database đã được tạo trước đó.
-- Backend đọc bảng outbox_events và gửi WebSocket đúng tài khoản.
-- Các trigger đều chỉ có một câu lệnh để import được bằng phpMyAdmin/XAMPP.
-- ============================================================================

USE `gym_db`;

DROP TRIGGER IF EXISTS `trg_checkins_after_insert`;
CREATE TRIGGER `trg_checkins_after_insert`
AFTER INSERT ON `checkins`
FOR EACH ROW
INSERT INTO `outbox_events`
  (`event_type`, `aggregate_type`, `aggregate_id`, `target_user_id`, `payload_json`, `status`, `available_at`, `created_at`)
SELECT
  'checkin.confirmed',
  'checkin',
  CAST(NEW.id AS CHAR),
  CASE
    WHEN NEW.member_id IS NOT NULL THEN (SELECT user_id FROM members WHERE id = NEW.member_id LIMIT 1)
    WHEN NEW.trainer_id IS NOT NULL THEN (SELECT user_id FROM trainers WHERE id = NEW.trainer_id LIMIT 1)
    ELSE NULL
  END,
  JSON_OBJECT(
    'checkin_id', NEW.id,
    'member_id', NEW.member_id,
    'trainer_id', NEW.trainer_id,
    'status', NEW.status,
    'scanned_at', DATE_FORMAT(NEW.scanned_at, '%Y-%m-%dT%H:%i:%s'),
    'pair_group_id', NEW.pair_group_id
  ),
  'pending', NOW(), NOW();

DROP TRIGGER IF EXISTS `trg_notifications_after_insert`;
CREATE TRIGGER `trg_notifications_after_insert`
AFTER INSERT ON `notifications`
FOR EACH ROW
INSERT INTO `outbox_events`
  (`event_type`, `aggregate_type`, `aggregate_id`, `target_user_id`, `payload_json`, `status`, `available_at`, `created_at`)
VALUES
  ('notification.created', 'notification', CAST(NEW.id AS CHAR), NEW.user_id,
   JSON_OBJECT(
     'notification_id', NEW.id,
     'type', NEW.type,
     'title', NEW.title,
     'created_at', DATE_FORMAT(NEW.created_at, '%Y-%m-%dT%H:%i:%s')
   ),
   'pending', NOW(), NOW());

DROP TRIGGER IF EXISTS `trg_schedules_after_insert`;
CREATE TRIGGER `trg_schedules_after_insert`
AFTER INSERT ON `training_schedules`
FOR EACH ROW
INSERT INTO `outbox_events`
  (`event_type`, `aggregate_type`, `aggregate_id`, `target_user_id`, `payload_json`, `status`, `available_at`, `created_at`)
SELECT
  'schedule.created', 'training_schedule', CAST(NEW.id AS CHAR), m.user_id,
  JSON_OBJECT('schedule_id', NEW.id, 'member_id', NEW.member_id, 'trainer_id', NEW.trainer_id, 'status', NEW.status),
  'pending', NOW(), NOW()
FROM members m WHERE m.id = NEW.member_id
UNION ALL
SELECT
  'schedule.created', 'training_schedule', CAST(NEW.id AS CHAR), t.user_id,
  JSON_OBJECT('schedule_id', NEW.id, 'member_id', NEW.member_id, 'trainer_id', NEW.trainer_id, 'status', NEW.status),
  'pending', NOW(), NOW()
FROM trainers t WHERE t.id = NEW.trainer_id;

DROP TRIGGER IF EXISTS `trg_schedules_after_update`;
CREATE TRIGGER `trg_schedules_after_update`
AFTER UPDATE ON `training_schedules`
FOR EACH ROW
INSERT INTO `outbox_events`
  (`event_type`, `aggregate_type`, `aggregate_id`, `target_user_id`, `payload_json`, `status`, `available_at`, `created_at`)
SELECT
  IF(NEW.status = 'cancelled' AND OLD.status <> 'cancelled', 'schedule.cancelled', 'schedule.updated'),
  'training_schedule', CAST(NEW.id AS CHAR), m.user_id,
  JSON_OBJECT('schedule_id', NEW.id, 'member_id', NEW.member_id, 'trainer_id', NEW.trainer_id, 'status', NEW.status),
  'pending', NOW(), NOW()
FROM members m WHERE m.id = NEW.member_id
UNION ALL
SELECT
  IF(NEW.status = 'cancelled' AND OLD.status <> 'cancelled', 'schedule.cancelled', 'schedule.updated'),
  'training_schedule', CAST(NEW.id AS CHAR), t.user_id,
  JSON_OBJECT('schedule_id', NEW.id, 'member_id', NEW.member_id, 'trainer_id', NEW.trainer_id, 'status', NEW.status),
  'pending', NOW(), NOW()
FROM trainers t WHERE t.id = NEW.trainer_id;

DROP TRIGGER IF EXISTS `trg_member_packages_after_insert`;
CREATE TRIGGER `trg_member_packages_after_insert`
AFTER INSERT ON `member_packages`
FOR EACH ROW
INSERT INTO `outbox_events`
  (`event_type`, `aggregate_type`, `aggregate_id`, `target_user_id`, `payload_json`, `status`, `available_at`, `created_at`)
SELECT
  'membership.updated', 'member_package', CAST(NEW.id AS CHAR), m.user_id,
  JSON_OBJECT(
    'member_package_id', NEW.id, 'member_id', NEW.member_id, 'trainer_id', NEW.pt_id,
    'sessions_remaining', NEW.sessions_remaining, 'status', NEW.status,
    'end_date', DATE_FORMAT(NEW.end_date, '%Y-%m-%d')
  ),
  'pending', NOW(), NOW()
FROM members m WHERE m.id = NEW.member_id
UNION ALL
SELECT
  'membership.updated', 'member_package', CAST(NEW.id AS CHAR), t.user_id,
  JSON_OBJECT(
    'member_package_id', NEW.id, 'member_id', NEW.member_id, 'trainer_id', NEW.pt_id,
    'sessions_remaining', NEW.sessions_remaining, 'status', NEW.status,
    'end_date', DATE_FORMAT(NEW.end_date, '%Y-%m-%d')
  ),
  'pending', NOW(), NOW()
FROM trainers t WHERE NEW.pt_id IS NOT NULL AND t.id = NEW.pt_id;

DROP TRIGGER IF EXISTS `trg_member_packages_after_update`;
CREATE TRIGGER `trg_member_packages_after_update`
AFTER UPDATE ON `member_packages`
FOR EACH ROW
INSERT INTO `outbox_events`
  (`event_type`, `aggregate_type`, `aggregate_id`, `target_user_id`, `payload_json`, `status`, `available_at`, `created_at`)
SELECT
  IF(NOT (OLD.sessions_remaining <=> NEW.sessions_remaining), 'membership.sessions_changed', 'membership.updated'),
  'member_package', CAST(NEW.id AS CHAR), m.user_id,
  JSON_OBJECT(
    'member_package_id', NEW.id, 'member_id', NEW.member_id, 'trainer_id', NEW.pt_id,
    'sessions_remaining', NEW.sessions_remaining, 'status', NEW.status,
    'end_date', DATE_FORMAT(NEW.end_date, '%Y-%m-%d')
  ),
  'pending', NOW(), NOW()
FROM members m WHERE m.id = NEW.member_id
UNION ALL
SELECT
  IF(NOT (OLD.sessions_remaining <=> NEW.sessions_remaining), 'membership.sessions_changed', 'membership.updated'),
  'member_package', CAST(NEW.id AS CHAR), t.user_id,
  JSON_OBJECT(
    'member_package_id', NEW.id, 'member_id', NEW.member_id, 'trainer_id', NEW.pt_id,
    'sessions_remaining', NEW.sessions_remaining, 'status', NEW.status,
    'end_date', DATE_FORMAT(NEW.end_date, '%Y-%m-%d')
  ),
  'pending', NOW(), NOW()
FROM trainers t WHERE NEW.pt_id IS NOT NULL AND t.id = NEW.pt_id;

DROP TRIGGER IF EXISTS `trg_pt_sessions_after_insert`;
CREATE TRIGGER `trg_pt_sessions_after_insert`
AFTER INSERT ON `pt_sessions`
FOR EACH ROW
INSERT INTO `outbox_events`
  (`event_type`, `aggregate_type`, `aggregate_id`, `target_user_id`, `payload_json`, `status`, `available_at`, `created_at`)
SELECT
  'pt_session.created', 'pt_session', CAST(NEW.id AS CHAR), m.user_id,
  JSON_OBJECT(
    'pt_session_id', NEW.id, 'member_id', NEW.member_id,
    'trainer_id', NEW.trainer_id, 'status', NEW.status
  ),
  'pending', NOW(), NOW()
FROM members m WHERE m.id = NEW.member_id
UNION ALL
SELECT
  'trainer.kpi_changed', 'pt_session', CAST(NEW.id AS CHAR), t.user_id,
  JSON_OBJECT(
    'pt_session_id', NEW.id, 'member_id', NEW.member_id,
    'trainer_id', NEW.trainer_id, 'commission_amount', NEW.commission_amount
  ),
  'pending', NOW(), NOW()
FROM trainers t WHERE t.id = NEW.trainer_id;

-- Đưa event bị kẹt do backend tắt đột ngột về trạng thái chờ gửi.
UPDATE `outbox_events`
SET `status` = 'pending'
WHERE `status` = 'processing';
