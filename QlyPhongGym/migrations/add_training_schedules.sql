USE `gym_db`;

CREATE TABLE IF NOT EXISTS `training_schedules` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `trainer_id` INT NOT NULL,
  `member_id` INT NOT NULL,
  `member_package_id` INT NULL,
  `title` VARCHAR(200) NOT NULL,
  `start_at` DATETIME NOT NULL,
  `end_at` DATETIME NOT NULL,
  `location` VARCHAR(200) NULL,
  `note` TEXT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'upcoming',
  `created_by` INT NULL,
  `cancelled_by` INT NULL,
  `cancelled_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_schedule_trainer_time` (`trainer_id`, `start_at`, `status`),
  KEY `idx_schedule_member_time` (`member_id`, `start_at`, `status`),
  CONSTRAINT `fk_schedule_trainer_patch`
    FOREIGN KEY (`trainer_id`) REFERENCES `trainers` (`id`),
  CONSTRAINT `fk_schedule_member_patch`
    FOREIGN KEY (`member_id`) REFERENCES `members` (`id`),
  CONSTRAINT `fk_schedule_member_package_patch`
    FOREIGN KEY (`member_package_id`) REFERENCES `member_packages` (`id`),
  CONSTRAINT `fk_schedule_created_by_patch`
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_schedule_cancelled_by_patch`
    FOREIGN KEY (`cancelled_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
