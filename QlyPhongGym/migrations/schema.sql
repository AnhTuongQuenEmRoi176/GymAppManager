-- Migration mẫu: tạo các bảng chính
CREATE TABLE IF NOT EXISTS roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(200),
  phone VARCHAR(20),
  email VARCHAR(150),
  role_id INT,
  avatar VARCHAR(500),
  is_active TINYINT(1) DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS trainers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNIQUE,
  specialty VARCHAR(200),
  start_date DATE,
  end_date DATE NULL,
  base_salary DECIMAL(12,2) DEFAULT 0.00,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS members (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNIQUE,
  dob DATE NULL,
  gender ENUM('Nam','Nữ','Khác'),
  address VARCHAR(255),
  joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  status ENUM('active','inactive','suspended') DEFAULT 'active',
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS packages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150),
  price DECIMAL(12,2) NOT NULL,
  duration_days INT NOT NULL,
  sessions INT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS member_packages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT,
  package_id INT,
  start_date DATE,
  end_date DATE,
  sessions_remaining INT NULL,
  pt_id INT NULL,
  price_paid DECIMAL(12,2),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (package_id) REFERENCES packages(id)
);

CREATE TABLE IF NOT EXISTS checkins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  member_id INT NULL,
  trainer_id INT NULL,
  scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  scanner_user_id INT NULL,
  source VARCHAR(50),
  qr_payload VARCHAR(500),
  photo VARCHAR(500) NULL,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (trainer_id) REFERENCES trainers(id)
);

CREATE TABLE IF NOT EXISTS qr_demo (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(255) UNIQUE,
  entity_type ENUM('member','trainer'),
  entity_id INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pt_sessions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  trainer_id INT,
  member_id INT,
  session_date DATETIME,
  confirmed_by INT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  type ENUM('payment','salary','refund','other'),
  amount DECIMAL(12,2),
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  description TEXT,
  created_by INT
);
