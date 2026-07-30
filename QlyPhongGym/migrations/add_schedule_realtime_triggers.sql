USE `gym_db`;

-- Chỉ chạy file này khi database đã có bảng outbox_events của backend FastAPI.
-- Trigger giúp lịch được tạo/sửa trực tiếp từ Windows App vẫn đẩy realtime sang Flutter.

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
