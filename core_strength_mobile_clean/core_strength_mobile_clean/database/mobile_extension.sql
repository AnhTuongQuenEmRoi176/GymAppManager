-- =========================================================
-- CORE STRENGTH - Mở rộng database cho Flutter Mobile
-- Chạy sau schema hiện tại. Kiểm tra trên DB test trước khi production.
-- =========================================================

-- 1. Role cho ứng dụng mobile
INSERT IGNORE INTO roles(name) VALUES ('MEMBER'), ('TRAINER');

-- 2. Bổ sung index cần thiết cho tài khoản
ALTER TABLE users
  ADD INDEX idx_users_phone (phone),
  ADD INDEX idx_users_email (email),
  ADD INDEX idx_users_role_active (role_id, is_active);

-- 3. Refresh token để quản lý phiên đăng nhập
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token_hash VARCHAR(255) NOT NULL,
  expires_at DATETIME NOT NULL,
  revoked_at DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  device_name VARCHAR(150) NULL,
  UNIQUE KEY uq_refresh_token_hash (token_hash),
  INDEX idx_refresh_user (user_id, revoked_at, expires_at),
  CONSTRAINT fk_refresh_user FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
);

-- 4. QR động, hết hạn và dùng một lần
CREATE TABLE IF NOT EXISTS qr_tokens (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  token_id CHAR(36) NOT NULL,
  user_id INT NOT NULL,
  entity_type ENUM('member','trainer') NOT NULL,
  entity_id INT NOT NULL,
  token_hash VARCHAR(255) NOT NULL,
  expires_at DATETIME NOT NULL,
  used_at DATETIME NULL,
  used_by INT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_qr_token_id (token_id),
  UNIQUE KEY uq_qr_token_hash (token_hash),
  INDEX idx_qr_lookup (user_id, expires_at, used_at),
  CONSTRAINT fk_qr_user FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_qr_used_by FOREIGN KEY (used_by) REFERENCES users(id)
    ON DELETE SET NULL
);

-- 5. Lịch tập/lịch dạy tương lai
CREATE TABLE IF NOT EXISTS training_schedules (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  trainer_id INT NOT NULL,
  member_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  start_at DATETIME NOT NULL,
  end_at DATETIME NOT NULL,
  location VARCHAR(200) NULL,
  note TEXT NULL,
  status ENUM('upcoming','completed','cancelled') DEFAULT 'upcoming',
  created_by INT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_schedule_trainer_time (trainer_id, start_at, status),
  INDEX idx_schedule_member_time (member_id, start_at, status),
  CONSTRAINT fk_schedule_trainer FOREIGN KEY (trainer_id) REFERENCES trainers(id),
  CONSTRAINT fk_schedule_member FOREIGN KEY (member_id) REFERENCES members(id),
  CONSTRAINT fk_schedule_creator FOREIGN KEY (created_by) REFERENCES users(id)
    ON DELETE SET NULL
);

-- 6. Thông báo trong ứng dụng
CREATE TABLE IF NOT EXISTS notifications (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  type VARCHAR(50) NOT NULL,
  title VARCHAR(200) NOT NULL,
  body TEXT NOT NULL,
  data_json JSON NULL,
  is_read TINYINT(1) DEFAULT 0,
  read_at DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_notification_user (user_id, is_read, created_at),
  CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
);

-- 7. Token thiết bị cho Firebase Cloud Messaging
CREATE TABLE IF NOT EXISTS device_tokens (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token VARCHAR(500) NOT NULL,
  platform ENUM('android','ios','web') NOT NULL,
  device_name VARCHAR(150) NULL,
  is_active TINYINT(1) DEFAULT 1,
  last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_device_token (token),
  INDEX idx_device_user_active (user_id, is_active),
  CONSTRAINT fk_device_user FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
);

-- 8. Bổ sung trường chống trùng và trạng thái cho check-in
-- MySQL không hỗ trợ ADD COLUMN IF NOT EXISTS trên mọi phiên bản cũ.
-- Chỉ chạy các câu ALTER dưới đây nếu cột chưa tồn tại.

-- ALTER TABLE checkins
--   ADD COLUMN status ENUM('pending','confirmed','rejected') DEFAULT 'confirmed',
--   ADD COLUMN confirmed_at DATETIME NULL,
--   ADD COLUMN pair_group_id CHAR(36) NULL,
--   ADD COLUMN idempotency_key VARCHAR(100) NULL,
--   ADD COLUMN device_id VARCHAR(150) NULL,
--   ADD UNIQUE KEY uq_checkin_idempotency (idempotency_key),
--   ADD INDEX idx_checkin_pair (pair_group_id),
--   ADD CONSTRAINT fk_checkin_scanner FOREIGN KEY (scanner_user_id)
--     REFERENCES users(id) ON DELETE SET NULL;

-- 9. Hoàn thiện foreign key còn thiếu trong schema SQL cũ
-- Chỉ chạy khi dữ liệu hiện tại không vi phạm ràng buộc.

-- ALTER TABLE member_packages
--   ADD CONSTRAINT fk_member_package_pt FOREIGN KEY (pt_id)
--     REFERENCES trainers(id) ON DELETE SET NULL;

-- ALTER TABLE pt_sessions
--   ADD CONSTRAINT fk_pt_session_trainer FOREIGN KEY (trainer_id)
--     REFERENCES trainers(id),
--   ADD CONSTRAINT fk_pt_session_member FOREIGN KEY (member_id)
--     REFERENCES members(id),
--   ADD CONSTRAINT fk_pt_session_confirmed_by FOREIGN KEY (confirmed_by)
--     REFERENCES users(id) ON DELETE SET NULL;

-- ALTER TABLE transactions
--   ADD CONSTRAINT fk_transaction_created_by FOREIGN KEY (created_by)
--     REFERENCES users(id) ON DELETE SET NULL;
