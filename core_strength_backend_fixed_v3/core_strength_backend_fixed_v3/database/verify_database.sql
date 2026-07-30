USE `gym_db`;

SELECT 'roles' AS item, COUNT(*) AS total FROM roles
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'members', COUNT(*) FROM members
UNION ALL SELECT 'trainers', COUNT(*) FROM trainers
UNION ALL SELECT 'packages', COUNT(*) FROM packages
UNION ALL SELECT 'member_packages', COUNT(*) FROM member_packages
UNION ALL SELECT 'training_schedules', COUNT(*) FROM training_schedules
UNION ALL SELECT 'checkins', COUNT(*) FROM checkins
UNION ALL SELECT 'pt_sessions', COUNT(*) FROM pt_sessions
UNION ALL SELECT 'notifications', COUNT(*) FROM notifications
UNION ALL SELECT 'outbox_events', COUNT(*) FROM outbox_events;

SHOW TRIGGERS FROM `gym_db`;

SELECT id, username, full_name, phone, email, role_id, is_active
FROM users
ORDER BY id;
