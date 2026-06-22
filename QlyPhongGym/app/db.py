from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Đường dẫn tới thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent.parent

# Load file .env
load_dotenv(BASE_DIR / ".env")

# Đọc cấu hình database
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER", "root")

# Hỗ trợ cả DB_PASSWORD và DB_PASS
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS", "")

# Kiểm tra cấu hình bắt buộc
if not DB_NAME:
    raise ValueError(
        "Thiếu DB_NAME trong file .env"
    )

# Chuỗi kết nối MySQL
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

# Tạo engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Tạo session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_session():
    return SessionLocal()