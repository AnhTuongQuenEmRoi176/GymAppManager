# Cấu trúc thư mục dự án (Python/PyQt6)
gym_management/
├── main.py                 # File chạy chính
├── database/
│   ├── connection.py       # Kết nối MySQL
│   └── schema.sql          # Cấu trúc Database
├── assets/
│   ├── images/             # Ảnh đại diện, logo
│   └── icons/              # Icon giao diện
├── modules/
│   ├── auth.py             # Đăng nhập/Đăng ký (bcrypt)
│   ├── qr_scanner.py       # Xử lý OpenCV & QR
│   └── excel_exporter.py   # Xuất file pandas/openpyxl
└── ui/
    ├── tab_dashboard.py    # Trang chủ & Quét QR
    ├── tab_pt.py           # Quản lý PT
    ├── tab_members.py      # Quản lý Hội viên
    ├── tab_packages.py     # Quản lý Gói tập
    ├── tab_history.py      # Lịch sử Check-in
    └── tab_reports.py      # Thống kê doanh thu (Admin)

# Database Schema (MySQL)
CREATE DATABASE gym_db;

CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(100),
    role ENUM('Admin', 'Receptionist'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PTs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    phone VARCHAR(20),
    specialty VARCHAR(100),
    base_salary DECIMAL(10,2),
    avatar_url VARCHAR(255),
    hire_date DATE,
    status ENUM('Active', 'Resigned')
);

CREATE TABLE Members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    phone VARCHAR(20),
    avatar_url VARCHAR(255),
    qr_code VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Packages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    price DECIMAL(10,2),
    duration_days INT,
    pt_included BOOLEAN
);

CREATE TABLE MemberSubscriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT,
    package_id INT,
    pt_id INT NULL,
    start_date DATE,
    end_date DATE,
    pt_sessions_total INT DEFAULT 0,
    pt_sessions_left INT DEFAULT 0,
    FOREIGN KEY (member_id) REFERENCES Members(id),
    FOREIGN KEY (package_id) REFERENCES Packages(id)
);

CREATE TABLE CheckInHistory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT,
    pt_id INT NULL,
    checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    receptionist_id INT,
    FOREIGN KEY (member_id) REFERENCES Members(id),
    FOREIGN KEY (receptionist_id) REFERENCES Users(id)
);