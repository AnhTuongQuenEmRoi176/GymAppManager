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
